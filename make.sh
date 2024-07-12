#!/bin/bash

if [[ "$1" == "" ]]; then
	# Build all `md` files
	for f in *.md; do
		echo "Building: $f"
		bn="$(basename "$f" .md)"
	done
	echo "Built all documents. Calculating hashes..."
	cd export/ || exit

	echo "Calculated hashes. Signing generated files..."
	for f in ./*; do
		echo "Signing: $f"
		# verify with `gpg --verify <file>.asc <file>`
		gpg --default-key C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2 --armor --detach-sign --sign "$f"
		# verify with `minisign -Vm <file> -P RWQ0WYJ07DUokK8V/6LNJ9bf/O/QM9k4FSlDmzgEeXm7lEpw3ecYjXDM`
		yes '' | minisign -S -s /home/user/.minisign/minisign.key -m "$f"
	done
	cd ../ || exit
	# Sign original *.md files
	for MDFILE in ./*.md; do
		echo "Signing: $MDFILE"
		# verify with GPG
		gpg --default-key C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2 --armor --detach-sign --sign "$MDFILE"
		# verify with `minisign -Vm <file> -P RWQ0WYJ07DUokK8V/6LNJ9bf/O/QM9k4FSlDmzgEeXm7lEpw3ecYjXDM`
		yes '' | minisign -S -s /home/user/.minisign/minisign.key -m "$MDFILE"
	done
	cp /home/user/KEY_ROTATION.md.asc ./KEY_ROTATION.md.asc
	cp /home/user/KEY_ROTATION.md.minisig ./KEY_ROTATION.md.minisig
	mv *.asc export/
	cp *.md export/
	cd export/ || exit
	sha256sum *.md >> sha256sum.txt
	gpg --default-key C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2 --armor --detach-sign sha256sum.txt
	yes '' | minisign -S -s /home/user/.minisign/minisign.key -m sha256sum.txt
	b2sum *.md >> b2sum.txt
	gpg --default-key C3023DBEA3FB38C438BA1EEDCEC60AEDE8B992A2 --armor --detach-sign b2sum.txt
	yes '' | minisign -S -s /home/user/.minisign/minisign.key -m b2sum.txt
	
	cd ../ || exit
	mv *.md.minisig export/
	echo "Signed and exported all files."
	echo "Done."
	exit
fi

# bn="$1"

# echo "Generating HTML..."
# pandoc --embed-resources --standalone "$bn".md -o export/"$bn".html --metadata title="The Hitchhiker's Guide to Online Anonymity"
# echo "Generating PDF..."
# pandoc --embed-resources --standalone "$bn".md -o export/"$bn".pdf --metadata title="The Hitchhiker's Guide to Online Anonymity" -t context

# go run md2pdf -i guide.md \
#     -o guide.pdf \
#     -s ~/.config/zaje/syntax_files \
#     --theme dark \
#     --new-page-on-hr \
#     --with-footer \
#     --author "Anonymous Planet <contact@anonymousplanet.org>" \
#     --title "The Hitchhiker's Guide to Online Anonymity"

# echo "Generating ODT..."
# pandoc --embed-resources --standalone "$bn".md -o export/"$bn".odt --metadata title="The Hitchhiker's Guide to Online Anonymity"
