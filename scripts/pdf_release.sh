!/bin/bash
set -e

# PDF Hashing, Scanning, Release and Management script (hSCRAM)
# Usage: ./pdf_release.sh --build <light|dark|both> --release <tag|latest> [--vt-api-key]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
EXPORT_DIR="$ROOT_DIR/export"

# Default values
MODE="both"  # light, dark, or both
RELEASE_MODE="tag"  # tag (e.g. "v2.1.2") or "latest"
VT_API_KEY=""
GITHUB_TOKEN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            MODE="$2"
            shift 2
            ;;
        --release)
            RELEASE_MODE="$2"
            shift 2
            ;;
        --vt-api-key)
            VT_API_KEY="$2"
            shift 2
            ;;
        --github-token)
            GITHUB_TOKEN="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ ! "$MODE" =~ ^(light|dark|both)$ ]]; then
    echo "Error: Invalid build mode '$MODE'. Must be 'light', 'dark', or 'both'."
    exit 1
fi

echo "Hashing, Scanning, Release and Management script (hSCRAM)"
echo "Mode: $MODE"
echo "Release Mode: $RELEASE_MODE"

generate_hash() {
    local file="$1"
    sha256sum "$file" | cut -d' ' -f1
}

create_hash_file() {
    local pdf_path="$1"
    local base_name=$(basename "$pdf_path")
    local hash_file="${EXPORT_DIR}/${base_name}.sha256"
    
    (cd "$EXPORT_DIR" && sha256sum "$base_name") > "$hash_file"
    echo "Created: $hash_file"
}

scan_with_virustotal() {
    local pdf_path="$1"
    local base_name=$(basename "$pdf_path")
    
    if [[ -z "$VT_API_KEY" ]]; then
        echo "Warning: VT_API_KEY not provided, skipping VirusTotal scan for $base_name"
        return 1
    fi
    
    echo "Scanning $base_name with VirusTotal..."
    
    local upload_response=$(curl -s -X POST \
        -H "x-apikey: $VT_API_KEY" \
        -F "file=@$pdf_path" \
        https://www.virustotal.com/api/v3/files)
    
    if [[ $? -ne 0 ]]; then
        echo "Error uploading $base_name to VirusTotal"
        return 1
    fi
    
    local file_id=$(echo "$upload_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null || echo "")
    
    if [[ -z "$file_id" ]]; then
        echo "Error: Could not extract file ID from VirusTotal response for $base_name"
        echo "Response: $upload_response"
        return 1
    fi
    
    local vt_url="https://www.virustotal.com/gui/file/$file_id"
    echo "$vt_url"
}

scan_all_pdfs() {
    local results_file="$EXPORT_DIR/virus-total-results.md"
    
    cat > "$results_file" << 'HEADER'
## VirusTotal Scan Results

**Scan Date:** TIMESTAMP

---
HEADER
    
    sed -i "s/TIMESTAMP/$(date -u +"%Y-%m-%d %H:%M UTC")/" "$results_file"
    
    local pdf_files=()
    if [[ "$MODE" == "light" || "$MODE" == "both" ]]; then
        pdf_files+=("$EXPORT_DIR/thgtoa.pdf")
    fi
    if [[ "$MODE" == "dark" || "$MODE" == "both" ]]; then
        pdf_files+=("$EXPORT_DIR/thgtoa-dark.pdf")
    fi
    
    for pdf in "${pdf_files[@]}"; do
        if [[ -f "$pdf" ]]; then
            local base_name=$(basename "$pdf")
            local hash=$(generate_hash "$pdf")
            
            echo "" >> "$results_file"
            echo "### $base_name" >> "$results_file"
            echo "- **SHA256 Hash:** \`$hash\`" >> "$results_file"
            
            if [[ -n "$VT_API_KEY" ]]; then
                local vt_url=$(scan_with_virustotal "$pdf")
                if [[ $? -eq 0 && -n "$vt_url" ]]; then
                    echo "- **VirusTotal Report:** [$vt_url]($vt_url)" >> "$results_file"
                else
                    echo "- **VirusTotal Report:** Scan failed or API key not provided" >> "$results_file"
                fi
            else
                echo "- **VirusTotal Report:** VT_API_KEY not configured, scan skipped" >> "$results_file"
            fi
            
            create_hash_file "$pdf"
        else
            echo "Warning: $pdf does not exist, skipping..."
        fi
    done
    
    cat >> "$results_file" << 'FOOTER'

---
*Scan performed automatically by GitHub Actions*
FOOTER
    
    echo "VirusTotal results saved to: $results_file"
}

update_release() {
    local tag="${1:-}"
    local release_notes="$EXPORT_DIR/release-notes.md"
    
    if [[ "$RELEASE_MODE" == "tag" && -z "$tag" ]]; then
        tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    fi
    
    if [[ -z "$tag" ]]; then
        echo "Warning: No release tag found, skipping release update."
        return 1
    fi
    
    echo "Updating release for tag: $tag"
    
    cat > "$release_notes" << EOF
# Release Notes - $tag

**Release Date:** $(date -u +"%Y-%m-%d %H:%M UTC")

## PDF Files

EOF
    
    if [[ "$MODE" == "light" || "$MODE" == "both" ]]; then
        local hash=$(generate_hash "$EXPORT_DIR/thgtoa.pdf")
        echo "- **thgtoa.pdf (Light Mode)**" >> "$release_notes"
        echo "  - SHA256: \`$hash\`" >> "$release_notes"
        if [[ -f "$EXPORT_DIR/thgtoa.pdf.sig" ]]; then
            echo "  - Signature: \`thgtoa.pdf.sig\` (GPG signed)" >> "$release_notes"
        fi
    fi
    
    if [[ "$MODE" == "dark" || "$MODE" == "both" ]]; then
        local hash=$(generate_hash "$EXPORT_DIR/thgtoa-dark.pdf")
        echo "- **thgtoa-dark.pdf (Dark Mode)**" >> "$release_notes"
        echo "  - SHA256: \`$hash\`" >> "$release_notes"
        if [[ -f "$EXPORT_DIR/thgtoa-dark.pdf.sig" ]]; then
            echo "  - Signature: \`thgtoa-dark.pdf.sig\` (GPG signed)" >> "$release_notes"
        fi
    fi
    
    echo "" >> "$release_notes"
    echo "---" >> "$release_notes"
    
    if [[ -f "$EXPORT_DIR/virus-total-results.md" ]]; then
        echo "## VirusTotal Scan Results" >> "$release_notes"
        echo "" >> "$release_notes"
        cat "$EXPORT_DIR/virus-total-results.md" >> "$release_notes"
        echo "" >> "$release_notes"
    fi
    
    local files_to_upload=""
    
    if [[ -f "$EXPORT_DIR/thgtoa.pdf" ]]; then
        files_to_upload+="$EXPORT_DIR/thgtoa.pdf "
    fi
    if [[ -f "$EXPORT_DIR/thgtoa-dark.pdf" ]]; then
        files_to_upload+="$EXPORT_DIR/thgtoa-dark.pdf "
    fi
    if [[ -f "$EXPORT_DIR/thgtoa.pdf.sig" ]]; then
        files_to_upload+="$EXPORT_DIR/thgtoa.pdf.sig "
    fi
    if [[ -f "$EXPORT_DIR/thgtoa-dark.pdf.sig" ]]; then
        files_to_upload+="$EXPORT_DIR/thgtoa-dark.pdf.sig "
    fi
    
    local combined_hash_file="$EXPORT_DIR/sha256sum-combined.txt"
    
    if [[ -f "$EXPORT_DIR/thgtoa.pdf.sha256" ]]; then
        cat "$EXPORT_DIR/thgtoa.pdf.sha256" >> "$combined_hash_file" 2>/dev/null || true
    fi
    if [[ -f "$EXPORT_DIR/thgtoa-dark.pdf.sha256" ]]; then
        echo "" >> "$combined_hash_file"
        cat "$EXPORT_DIR/thgtoa-dark.pdf.sha256" >> "$combined_hash_file"
    fi
    
    files_to_upload+="$combined_hash_file "
    
    if [[ -n "${GPG_PRIVATE_KEY:-}" && -n "${GPG_PASSPHRASE:-}" ]]; then
        echo "$GPG_PRIVATE_KEY" | gpg --batch --import 2>/dev/null || true
        gpg --batch --yes --armor --detach-sign --output "$combined_hash_file.sig" "$combined_hash_file" 2>/dev/null || true
        if [[ -f "$combined_hash_file.sig" ]]; then
            files_to_upload+="$combined_hash_file.sig "
        fi
    fi
    
    if command -v gh &> /dev/null && [[ -n "$GITHUB_TOKEN" ]]; then
        echo "Uploading release with GitHub CLI..."
        
        local release_exists=$(gh release view "$tag" 2>/dev/null && echo "yes" || echo "no")
        
        if [[ "$release_exists" == "yes" ]]; then
            gh release edit "$tag" --notes-file "$release_notes" 2>/dev/null || {
                echo "Warning: Failed to update release notes"
            }
            
            for file in $files_to_upload; do
                if [[ -f "$file" ]]; then
                    local file_name=$(basename "$file")
                    gh release upload "$tag" "$file" 2>/dev/null || {
                        echo "Warning: Failed to upload $file_name"
                    }
                fi
            done
        else
            gh release create "$tag" \
                --title "Release $tag" \
                --notes-file "$release_notes" \
                $files_to_upload 2>/dev/null || {
                    echo "Error: Failed to create release"
                    return 1
                }
        fi
        
    else
        if [[ -n "$GITHUB_TOKEN" && -n "$tag" ]]; then
            echo "Using GitHub API to upload release..."
            
            local repo="${GITHUB_REPOSITORY:-}"
            local api_url="https://api.github.com/repos/$repo/releases"
            
            local existing_release=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                "$api_url/tags/$tag")
            
            if [[ $(echo "$existing_release" | grep -c '"id":') -gt 0 ]]; then
                echo "Release already exists, updating..."
                local release_id=$(echo "$existing_release" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
                
                curl -X PATCH \
                    -H "Authorization: token $GITHUB_TOKEN" \
                    -H "Accept: application/vnd.github.v3+json" \
                    "$api_url/$release_id" \
                    -d "{\"body\":\"$(cat "$release_notes")\"}" 2>/dev/null || true
                
                for file in $files_to_upload; do
                    if [[ -f "$file" ]]; then
                        local file_name=$(basename "$file")
                        local mime_type=$(file --mime-type -b "$file")
                        
                        curl -X POST \
                            -H "Authorization: token $GITHUB_TOKEN" \
                            -H "Content-Type: $mime_type" \
                            --data-binary @"$file" \
                            "https://uploads.github.com/repos/$repo/releases/$release_id/assets?name=$file_name" 2>/dev/null || {
                                echo "Warning: Failed to upload $file_name"
                            }
                    fi
                done
            else
                echo "Creating new release..."
                
                local create_response=$(curl -s -X POST \
                    -H "Authorization: token $GITHUB_TOKEN" \
                    -H "Accept: application/vnd.github.v3+json" \
                    "$api_url" \
                    -d "{\"tag_name\":\"$tag\",\"name\":\"Release $tag\",\"body\":\"$(cat "$release_notes")\"}")
                
                local release_id=$(echo "$create_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
                
                for file in $files_to_upload; do
                    if [[ -f "$file" ]]; then
                        local file_name=$(basename "$file")
                        local mime_type=$(file --mime-type -b "$file")
                        
                        curl -X POST \
                            -H "Authorization: token $GITHUB_TOKEN" \
                            -H "Content-Type: $mime_type" \
                            --data-binary @"$file" \
                            "https://uploads.github.com/repos/$repo/releases/$release_id/assets?name=$file_name" 2>/dev/null || {
                                echo "Warning: Failed to upload $file_name"
                            }
                    fi
                done
            fi
        else
            echo "Error: GITHUB_TOKEN required for release upload."
            return 1
        fi
    fi
    
    echo "Release update complete!"
}

echo ""
echo "Step 1: Generating hashes..."
if [[ "$MODE" == "light" || "$MODE" == "both" ]]; then
    if [[ -f "$EXPORT_DIR/thgtoa.pdf" ]]; then
        create_hash_file "$EXPORT_DIR/thgtoa.pdf"
    else
        echo "Warning: $EXPORT_DIR/thgtoa.pdf not found. Ensure PDF is built first."
    fi
fi

if [[ "$MODE" == "dark" || "$MODE" == "both" ]]; then
    if [[ -f "$EXPORT_DIR/thgtoa-dark.pdf" ]]; then
        create_hash_file "$EXPORT_DIR/thgtoa-dark.pdf"
    else
        echo "Warning: $EXPORT_DIR/thgtoa-dark.pdf not found. Ensure PDF is built first."
    fi
fi

echo ""
echo "Step 2: Scanning with VirusTotal..."
scan_all_pdfs

echo ""
echo "Step 3: Updating release..."
update_release "$GITHUB_REF_NAME"

echo ""
echo "PDF Release Script Complete!"
