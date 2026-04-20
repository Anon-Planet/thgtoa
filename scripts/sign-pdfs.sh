#!/bin/bash

# Script to generate checksums (SHA256, B2SUM) and eventually GPG sign PDF files
# Usage: ./sign-pdfs.sh [input_directory] [output_directory]
# If directories are not provided, defaults will be used

set -e  # Exit on error

# Configuration
INPUT_DIR="${1:-./export}"           # Default: build-output directory
OUTPUT_DIR="${2:-./export}"           # Default: signed-pdfs directory
CHECKSUMS_DIR="${3:-./export}"          # Default: checksums directory
# GPG_KEY_ID="9FA5436D0EE360985157382517ECA05F768DEDF6"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create output directories
setup_directories() {
    print_info "Setting up directories..."

    if [ ! -d "$INPUT_DIR" ]; then
        print_error "Input directory '$INPUT_DIR' does not exist."
        exit 1
    fi

    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$CHECKSUMS_DIR"

    print_info "Input directory: $INPUT_DIR"
    print_info "Output directory: $OUTPUT_DIR"
    print_info "Checksums directory: $CHECKSUMS_DIR"
}

# Generate SHA256 checksum for a file
generate_sha256() {
    local file="$1"
    local filename=$(basename "$file")
    local output_file="${CHECKSUMS_DIR}/${filename}.sha256"

    sha256sum "$file" > "$output_file"
    print_info "SHA256 checksum generated: $output_file"
}

# Generate B2SUM checksum for a file
generate_b2sum() {
    local file="$1"
    local filename=$(basename "$file")
    local output_file="${CHECKSUMS_DIR}/${filename}.b2sum"

    b2sum "$file" > "$output_file"
    print_info "B2SUM checksum generated: $output_file"
}

# GPG sign a file
# gpg_sign() {
#     local file="$1"
#     local filename=$(basename "$file")

#     if [ -z "$GPG_KEY_ID" ]; then
#         print_warn "Skipping GPG signing for '$filename' (no key ID provided)"
#         return 0
#     fi

#     # Sign the file in detached mode with ASCII armor
#     gpg --batch --yes --detach-sign --armor --local-user "$GPG_KEY_ID" \
#         --output "${file}.sig" "$file"

#     print_info "GPG signature generated: ${file}.sig"
# }

# Process a single PDF file
process_pdf() {
    local pdf_file="$1"
    local filename=$(basename "$pdf_file")

    print_info "Processing: $filename"

    # Generate checksums
    generate_sha256 "$pdf_file"
    generate_b2sum "$pdf_file"
}

# Main function
main() {
    echo ""
    setup_directories

    # Find all PDF files in input directory (recursively)
    pdf_files=($(find "$INPUT_DIR" -type f -name "*.pdf"))

    if [ ${#pdf_files[@]} -eq 0 ]; then
        print_error "No PDF files found in '$INPUT_DIR'"
        exit 1
    fi

    print_info "Found ${#pdf_files[@]} PDF file(s) to process"

    # Process each PDF file
    for pdf_file in "${pdf_files[@]}"; do
        process_pdf "$pdf_file"
    done

    print_info "=========================================="
    print_info "Processing Complete!"
    print_info "=========================================="
    print_info "Checksums saved to: $CHECKSUMS_DIR"
    print_info "Signed files and signatures in: $(dirname "$INPUT_DIR")"

    # Display summary of checksums
    print_info "SHA256 Checksums:"
    cat "${CHECKSUMS_DIR}"/*.sha256 2>/dev/null || true
    print_info "B2SUM Checksums:"
    cat "${CHECKSUMS_DIR}"/*.b2sum 2>/dev/null || true
}

# Run main function
main "$@"
