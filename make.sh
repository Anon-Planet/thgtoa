#!/bin/bash

if [[ "$1" == "" ]]; then
	# Sign PDF
	mkdir -p upload/
	echo "Calculating hashes..."
	sha256sum ./*.pdf >> ./upload/sha256sum.txt
	b2sum ./*.pdf >> ./upload/b2sum.txt
	sha256sum ./*.odt >> ./upload/sha256sum.txt
	b2sum ./*.odt >> ./upload/b2sum.txt
	echo "Calculated hashes. Signing generated files..."
	for f in ./*.pdf; do
		echo "Signing PDFs: $f"
		# verify with GPG
		gpg --default-key 83A6CF9EF57AC25B5C7F5D29285E6048A12321B2 --armor --detach-sign --sign "$f"
		# verify with `minisign -Vm <file> -P RWQ0WYJ07DUokK8V/6LNJ9bf/O/QM9k4FSlDmzgEeXm7lEpw3ecYjXDM`
		yes '' | minisign -S -s /home/user/.minisign/minisign.key -m "$f"
	done
	for f in ./*.odt; do
		echo "Signing ODTs: $f"
		gpg --default-key 83A6CF9EF57AC25B5C7F5D29285E6048A12321B2 --armor --detach-sign --sign "$f"
		yes '' | minisign -S -s /home/user/.minisign/minisign.key -m "$f"
	done
	echo "All files cryptographically signed."
	cp /home/user/KEY_ROTATION.md.42FF35DB9DE7C088AB0FD4A70C216A52F6DF4920.asc ./KEY_ROTATION.md.asc
	cp /home/user/KEY_ROTATION.md.902835EC74825934.minisig ./KEY_ROTATION.md.minisig
	echo "Done."
	exit
fi

#bn="$1"
#
#echo "Generating HTML..."
#pandoc --self-contained "$bn".md -o upload/"$bn".html --metadata title="The Hitchhiker's Guide to Online Anonymity"
#echo "Generating PDF..."
#pandoc --self-contained "$bn".md -o upload/"$bn".pdf --metadata title="The Hitchhiker's Guide to Online Anonymity" -t context
#echo "Generating ODT..."
#pandoc --self-contained "$bn".md -o upload/"$bn".odt --metadata title="The Hitchhiker's Guide to Online Anonymity"

