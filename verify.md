## How to check ours (but also others from different projects) files for safety/integrity and authenticity:

The PDF and ODT files in this guide are cryptographically signed using GPG and [Minisign](https://jedisct1.github.io/minisign). Their integrity can be verified with the published SHA256 Checksum hashes on this website. SHA256 checksums of all the PDF and ODT files are available here in the [sha256sum.txt](sha256sum.txt) file. SHA256 Checksums, signatures, and VirusTotal ("VT") checks of the releases files (containing the whole repository) are available within the latest release information at <https://github.com/Anon-Planet/thgtoa/releases/latest> which will be available as soon as we have a stable release.

The GPG signatures for each PDF and ODT files are available here:
- <del>PDF (Light Theme) Main and Mirrors: [guide.pdf.asc](guide.pdf.asc)</del> (Currently unavailable)
- <del>ODT Main and Mirrors: [guide.odt.asc](guide.odt.asc)</del> (Currently unavailable)

The Minisign signatures for each PDF and ODT files are available here:
- <del>PDF (Light Theme) Main and Mirrors: [guide.pdf.minisig](guide.pdf.minisig)</del> (Currently unavailable)
- <del>ODT Main and Mirrors: [guide.odt.minisig](guide.odt.minisig)</del> (Currently unavailable)

### How to check the integrity of the files using the SHA256 Checksums:

First get the hash of your local file by following these steps for your OS:

Windows:
- From a command prompt, run ```certutil -hashfile filename.txt sha256```
- Compare the obtained hash result of your local file to the online files published hash. They should match.

MacOS:
- From a terminal, run ```shasum -a 256 /full/path/to/your/file```
- Compare the obtained hash result of your local file to the online file's published hash. They should match.

Linux:
- From a terminal, run ```sha256sum /full/path/to/your/file```
- Compare the obtained hash result of your local file to the online file's published hash. They should match.

All commits and releases on this repository are cryptographically signed, and verified using the same GPG key.

**Do check for the "Verified" tags on each commit or release.**

### How to verify the the authenticity, and integrity of the files using GPG:

To verify the files with GPG signatures, you should first install gpg on your system:
- Windows: Install gpg4win from <https://www.gpg4win.org/download.html>
- MacOS: Install GPG Tools from <https://gpgtools.org/>
- Linux: gpg should be installed by default

Import the GPG key from a trusted source of the publisher using the following command from a command prompt or terminal:

```gpg --auto-key-locate nodefault,wkd --locate-keys 42FF35DB9DE7C088AB0FD4A70C216A52F6DF4920```

In theory this command should fetch the key from the a default pool server. If this doesn't work, you can also download/view it directly from here (in our case): <https://anonymousplanet.org/42FF35DB9DE7C088AB0FD4A70C216A52F6DF4920.asc>

As well as the published key on any keyserver below (search for the fingerprint ```42FF35DB9DE7C088AB0FD4A70C216A52F6DF4920```):
- <https://pgp.mit.edu>
- <https://keys.openpgp.org>
- <https://keyserver.ubuntu.com>

You should then import it manually by issuing the following command on any OS:

```gpg --import 42FF35DB9DE7C088AB0FD4A70C216A52F6DF4920.asc```

Finally, verify the asc signature file (links above) against the PDF files by issuing the following commands:

```gpg --verify guide.pdf.asc guide.pdf"```

This should output a result showing it matches and is therefore a good result.

### How to verify the the authenticity, and integrity of the files using Minisign:

To verify the files with Minisign:

- You should first download minisign from <https://jedisct1.github.io/minisign/>.
- Download the files along with their \*.minisig signature file (these should be in the same directory).
- Download the Minisign public key available on the website and repository: [minisign.pub](minisign.pub) (again, place it in the same directory for convenience).
- Run the following command in a command prompt or terminal: ```minisign -Vm guide.pdf -p minisign.pub```.
- Output should show ```Signature and comment signature verified```.

### How to check the safety of the files using VT:
**Note: we not endorse VT. It should be used with extreme caution and never with any sensitive files due to their privacy policies.**

Temporarily Disabled. <del>The PDF and ODT files in this guide have been checked by VT, see the links below for an example but do not trust these hashes blindly. Check the hashes match and re-upload to VT if needed:
- PDF file: [[VT Scan]](https://www.virustotal.com/gui/file/21dfa2f7da668156275e4ca2bc82091f347739967a278cf24a062c15a3944016?nocache=1)
- ODT file: [[VT Scan]](https://www.virustotal.com/gui/file/df8554f732dc54b530fd831548f0727934f2e03ad1518ac33061d0995eab2172?nocache=1)</del> 

### Additional manual safety checks for the PDF files:

For additional safety, you can always double check the PDF files using the PDFID tool which you can download at <https://blog.didierstevens.com/programs/pdf-tools/>. (You might be wondering: "Why should I trust a random python script?" Well, it is open-source and well-known. It is also probably a safer bet than trusting a random PDF).

Here are the steps:

- Install latest 3.9.x version of Python on your OS, Download PDFID and, from a command prompt or terminal, run:

```python pdfid.py file-to-check.pdf```

And you should see the following entries at **0** for safety, this 0 means there is no Javascript or any action that could possibly execute malicious macros, scripts, etc. Normally this won't be necessary as most modern PDF readers won't execute those scripts anyway.

```bash
/JS                    0 #This indicates the presence of Javascript which could be malicious
/JavaScript            0 #This indicates the presence of Javascript which could be malicious
/AA                    0 #This indicates the presence of automatic action on opening
/OpenAction            0 #This indicates the presence of automatic action on opening
/AcroForm              0 #This indicates the presence of AcroForm which could contain malicious JavaScript
/JBIG2Decode           0 #This indicates the PDF uses JBIG2 compression which could be used for obfuscating malicious content
/RichMedia             0 #This indicates the presence rich media within the PDF such as Flash
/Launch                0 #This counts the launch actions
/EmbeddedFile          0 #This indicates there are embedded files within the PDF
/XFA                   0 #This indicates the presence of XML Forms within the PDF
```
