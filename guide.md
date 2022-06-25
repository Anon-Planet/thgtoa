# The Hitchhiker's Guide to Online Anonymity

(Or "How I learned to start worrying and love ~~privacy~~ anonymity")

Version 1.1.5, June 2022 by Anonymous Planet

**Forever in memory of Lena, 1999-2022**

#### **IMPORTANT RECOMMENDATION FOR UKRAINIANS. ВАЖЛИВА РЕКОМЕНДАЦІЯ ДЛЯ УКРАЇНЦІВ**

This is a message for the people of Ukraine.

We strongly recommend that you use Briar for communicating with people nearby.

You can find it here: <https://briarproject.org/>

With this application, you can communicate even when there is no internet.

--------------------------------------------------------------------------

Це послання до народу України.

Ми наполегливо рекомендуємо вам використовувати Briar для спілкування з людьми поблизу!

Ви можете знайти його тут: <https://briarproject.org/> і тут: <https://briarproject.org/quick-start/uk/>.

За допомогою цієї програми ви можете спілкуватися, навіть коли немає Інтернету.

--------------------------------------------------------------------------

**This guide is a work in progress**. While I am doing the best I can to correct issues, inaccuracies, and improve the content, general structure, and readability; it will probably never be "finished".

**There might be some wrong or outdated information in this guide because no human is omniscient, and humans do make mistakes.** **Please do not take this guide as a definitive gospel or truth because it is not. Mistakes have been written in the guide in earlier versions and fixed later when discovered. There are likely still some mistakes in this guide at this moment (hopefully few). Those are fixed as soon as possible when discovered.**

**This guide has been moved, due to recent unfortunate events. The old guide was at [anonymousplanet.org](https://web.archive.org/web/20220227172123/https://anonymousplanet.org/), but has since been moved to <https://anonymousplanet-ng.org>**

**Your experience may vary.** **Remember to check regularly for an updated version of this guide.**

This guide is a non-profit open-source initiative, licensed under Creative Commons **Attribution-NonCommercial** 4.0 International ([cc-by-nc-4.0][] <sup>[[Archive.org]][27]</sup>).

-   For mirrors see [Appendix A6: Mirrors]

-   For help in comparing versions see [Appendix A7: Comparing versions]

Feel free to submit issues **(please do report anything wrong)** using GitHub Issues at: <https://github.com/AnonyPla-ng/thgtoa/issues>

Feel free to come to discuss ideas at:

-   GitHub Discussions: <https://github.com/AnonyPla-ng/thgtoa/discussions>

-   <del>Rules for our chatrooms: <https://privacy-security-anonymity.github.io/chatrooms-rules/></del> (site is gone)

-   Matrix/Element Room: ```#anonymity:matrix.org``` <https://matrix.to/#/#anonymity:matrix.org>

-   Matrix Space regrouping several rooms with similar interests: ```#privacy-security-anonymity:matrix.org``` <https://matrix.to/#/#privacy-security-anonymity:matrix.org>.

Follow us on:

-   Twitter at <https://twitter.com/AnonyPla> (account recovered)

-   <del>Mastodon at <https://mastodon.social/@anonypla></del> (account gone)

To contact me, see the updated information on the website or send an e-mail to <contact@anonymousplanet-ng.org>

**Please consider [donating][Donations:] if you enjoy the project and want to support the hosting fees or support the funding of initiatives like the hosting of Tor Exit Nodes.**

There are several ways you could read this guide:

-   You want to understand the current state of online privacy and anonymity not necessarily get too technical about it: Just read the [Introduction][Introduction:], [Requirements][Pre-requisites and limitations:], [Understanding some basics of how some information can lead back to you and how to mitigate those][Understanding some basics of how some information can lead back to you and how to mitigate some:] and [A final editorial note][A small final editorial note:] sections.

-   You want to do the above but also learn how to remove some online information about you: Just read the above and add the [Removing some traces of your identities on search engines and various platforms.][Removing some traces of your identities on search engines and various platforms:]

-   You want to do the above and create online anonymous identities online safely and securely: Read the whole guide.

Precautions while reading this guide and accessing the various links:

-   **Documents/Files** have a **[Archive.org]** link next to them for accessing content through Archive.org for increased privacy and in case the content goes missing. Some links are not yet archived or outdated on archive.org in which case I encourage you to ask for a new save if possible.

-   **YouTube Videos** have a **[Invidious]** link next to them for accessing content through an Invidious Instance (in this case yewtu.be hosted in the Netherlands) for increased privacy. It is recommended to use these links when possible. See <https://github.com/iv-org/invidious> <sup>[[Archive.org]][29]</sup> for more information.

-   **Twitter** links have a **[Nitter]** link next to them for accessing content through a Nitter Instance (in this case nitter.net) for increased privacy. It is recommended to use these links when possible. See <https://github.com/zedeus/nitter> <sup>[[Archive.org]][30]</sup> for more information.

-   **Wikipedia** links have a **[Wikiless]** link next to them for accessing content through a Wikiless Instance (in this case Wikiless.org) for increased privacy. It is recommended to use these links when possible. See <https://codeberg.org/orenom/wikiless> <sup>[[Archive.org]][31]</sup> for more information.

-   **Medium** links have **[Scribe.rip]** link next to them for accessing content through a Scribe.rip Instance for increased privacy. Again, it is recommended to use these links when possible. See <https://scribe.rip/> <sup>[[Archive.org]][32]</sup> for more information.

-   If you are reading this in PDF or ODT format, you will notice plenty of \`\`\` in place of double quotes (""). These \`\`\` are there to ease conversion into Markdown/HTML format for online viewing of code blocks on the website.

If you do not want the hassle and use one of the browsers below, you could also just install the following extension on your browser: <https://libredirect.github.io/> <sup>[[Archive.org]][33]</sup>:

-   Firefox: <https://addons.mozilla.org/en-US/firefox/addon/libredirect/>

-   Chromium-based browsers (Chrome, Brave, Edge): <https://github.com/libredirect/libredirect/blob/master/chromium.md>

**If you are having trouble accessing any of the many academic articles referenced in this guide due to paywalls, feel free to use Sci-Hub (<https://en.wikipedia.org/wiki/Sci-Hub>** <sup>[[Wikiless]][34]</sup> <sup>[[Archive.org]][35]</sup>**) or LibGen (<https://en.wikipedia.org/wiki/Library_Genesis>** <sup>[[Wikiless]][36]</sup> <sup>[[Archive.org]][37]</sup>**) for finding and reading them. Because Science should be free. All of it. If you are faced with a paywall accessing some resources, consider using <https://12ft.io/>.**

Finally note that this guide does mention and even recommends various commercial services (such as VPNs, CDNs, e-mail providers, hosting providers...) **but is not endorsed or sponsored by any of them in any way. There are no referral links and no commercial ties with any of these providers. This project is 100% non-profit and only relying on donations.**

# Contents:

-   [Pre-requisites and limitations:]
    -   [Pre-requisites:]
    -   [Limitations:]
-   [Introduction:]
-   [Understanding some basics of how some information can lead back to you and how to mitigate some:]
    -   [Your Network:]
        -   [Your IP address:]
        -   [Your DNS and IP requests:]
        -   [Your RFID enabled devices:]
        -   [The Wi-Fi and Bluetooth devices around you:]
        -   [Malicious/Rogue Wi-Fi Access Points:]
        -   [Your Anonymized Tor/VPN traffic:]
        -   [Some Devices can be tracked even when offline:]
    -   [Your Hardware Identifiers:]
        -   [Your IMEI and IMSI (and by extension, your phone number):]
        -   [Your Wi-Fi or Ethernet MAC address:]
        -   [Your Bluetooth MAC address:]
    -   [Your CPU:]
    -   [Your Operating Systems and Apps telemetry services:]
    -   [Your Smart devices in general:]
    -   [Yourself:]
        -   [Your Metadata including your Geo-Location:]
        -   [Your Digital Fingerprint, Footprint, and Online Behavior:]
        -   [Your Clues about your Real Life and OSINT:]
        -   [Your Face, Voice, Biometrics, and Pictures:]
        -   [Phishing and Social Engineering:]
    -   [Malware, exploits, and viruses:]
        -   [Malware in your files/documents/e-mails:]
        -   [Malware and Exploits in your apps and services:]
        -   [Malicious USB devices:]
        -   [Malware and backdoors in your Hardware Firmware and Operating System:]
    -   [Your files, documents, pictures, and videos:]
        -   [Properties and Metadata:]
        -   [Watermarking:]
        -   [Pixelized or Blurred Information:]
    -   [Your Cryptocurrencies transactions:]
    -   [Your Cloud backups/sync services:]
    -   [Your Browser and Device Fingerprints:]
    -   [Local Data Leaks and Forensics:]
    -   [Bad Cryptography:]
    -   [No logging but logging anyway policies:]
    -   [Some Advanced targeted techniques:]
    -   [Some bonus resources:]
    -   [Notes:]
-   [General Preparations:]
    -   [Picking your route:]
        -   [Timing limitations:]
        -   [Budget/Material limitations:]
        -   [Skills:]
        -   [Adversarial considerations:]
    -   [Steps for all routes:]
        -   [Getting used to using better passwords:]
        -   [Getting an anonymous Phone number:]
        -   [Get a USB key:]
        -   [Find some safe places with decent public Wi-Fi:]
    -   [The Tor Browser route:]
        -   [Windows, Linux, and macOS:]
        -   [Android:]
        -   [iOS:]
        -   [Important Warning:]
    -   [The Tails route:]
        -   [Tor Browser settings on Tails:]
        -   [Persistent Plausible Deniability using Whonix within Tails:]
    -   [Steps for all other routes:]
        -   [Get a dedicated laptop for your sensitive activities:]
        -   [Some laptop recommendations:]
        -   [Bios/UEFI/Firmware Settings of your laptop:]
        -   [Physically Tamper protect your laptop:]
    -   [The Whonix route:]
        -   [Picking your Host OS (the OS installed on your laptop):]
        -   [Linux Host OS:]
        -   [macOS Host OS:]
        -   [Windows Host OS:]
        -   [Virtualbox on your Host OS:]
        -   [Pick your connectivity method:]
        -   [Getting an anonymous VPN/Proxy:]
        -   [Whonix:]
        -   [Tor over VPN:]
        -   [Whonix Virtual Machines:]
        -   [Pick your guest workstation Virtual Machine:]
        -   [Linux Virtual Machine (Whonix or Linux):]
        -   [Windows 10/11 Virtual Machine:]
        -   [Android Virtual Machine:]
        -   [macOS Virtual Machine:]
        -   [KeepassXC:]
        -   [VPN client installation (cash/Monero paid):]
        -   [(Optional) Allowing only the VMs to access the internet while cutting off the Host OS to prevent any leak:]
        -   [Final step:]
    -   [The Qubes Route:]
        -   [Pick your connectivity method:][1]
        -   [Getting an anonymous VPN/Proxy:][2]
        -   [Note about Plausible Deniability:]
        -   [Installation:]
        -   [Lid Closure Behavior:]
        -   [Connect to a Public Wi-Fi:]
        -   [Updating Qubes OS:]
        -   [Updating Whonix from version 15 to version 16:]
        -   [Hardening Qubes OS:]
        -   [Setup the VPN ProxyVM:]
        -   [Setup a safe Browser within Qubes OS (optional but recommended):]
        -   [Setup an Android VM:]
        -   [KeePassXC:][3]
-   [Creating your anonymous online identities:]
    -   [Understanding the methods used to prevent anonymity and verify identity:]
        -   [Captchas:]
        -   [Phone verification:]
        -   [E-Mail verification:]
        -   [User details checking:]
        -   [Proof of ID verification:]
        -   [IP Filters:]
        -   [Browser and Device Fingerprinting:]
        -   [Human interaction:]
        -   [User Moderation:]
        -   [Behavioral Analysis:]
        -   [Financial transactions:]
        -   [Sign-in with some platform:]
        -   [Live Face recognition and biometrics (again):]
        -   [Manual reviews:]
    -   [Getting Online:]
        -   [Creating new identities:]
        -   [Checking if your Tor Exit Node is terrible:]
        -   [The Real-Name System:]
        -   [About paid services:]
        -   [Overview:]
        -   [How to share files privately and/or chat anonymously:]
        -   [How to share files publicly but anonymously:]
        -   [Redacting Documents/Pictures/Videos/Audio safely:]
        -   [Communicating sensitive information to various known organizations:]
        -   [Maintenance tasks:]
-   [Backing up your work securely:]
    -   [Offline Backups:]
        -   [Selected Files Backups:]
        -   [Full Disk/System Backups:]
    -   [Online Backups:]
        -   [Files:]
        -   [Information:]
    -   [Synchronizing your files between devices Online:]
-   [Covering your tracks:]
    -   [Understanding HDD vs SSD:]
        -   [Wear-Leveling.]
        -   [Trim Operations:]
        -   [Garbage Collection:]
        -   [Conclusion:]
    -   [How to securely wipe your whole Laptop/Drives if you want to erase everything:]
        -   [Linux (all versions including Qubes OS):]
        -   [Windows:]
        -   [macOS:]
    -   [How to securely delete specific files/folders/data on your HDD/SSD and Thumb drives:]
        -   [Windows:][4]
        -   [Linux (non-Qubes OS):]
        -   [Linux (Qubes OS):]
        -   [macOS:][5]
    -   [Some additional measures against forensics:]
        -   [Removing Metadata from Files/Documents/Pictures:]
        -   [Tails:]
        -   [Whonix:][6]
        -   [macOS:][7]
        -   [Linux (Qubes OS):][8]
        -   [Linux (non-Qubes):]
        -   [Windows:][9]
    -   [Removing some traces of your identities on search engines and various platforms:]
        -   [Google:]
        -   [Bing:]
        -   [DuckDuckGo:]
        -   [Yandex:]
        -   [Qwant:]
        -   [Yahoo Search:]
        -   [Baidu:]
        -   [Wikipedia:]
        -   [Archive.today:]
        -   [Internet Archive:]
        -   [Others:]
-   [Some low-tech old-school tricks:]
    -   [Hidden communications in plain sight:]
    -   [How to spot if someone has been searching your stuff:]
-   [Some last OPSEC thoughts:]
-   [**If you think you got burned:**]
    -   [If you have some time:]
    -   [If you have no time:]
-   [A small final editorial note:]
-   [Donations:]
-   [Helping others staying anonymous:]
-   [Acknowledgments:]
-   [Appendix A: Windows Installation]
    -   [Installation:][10]
    -   [Privacy Settings:]
-   [Appendix B: Windows Additional Privacy Settings]
-   [Appendix C: Windows Installation Media Creation]
-   [Appendix D: Using System Rescue to securely wipe an SSD drive.]
-   [Appendix E: Clonezilla]
-   [Appendix F: Diskpart]
-   [Appendix G: Safe Browser on the Host OS]
    -   [If you can use Tor:]
    -   [If you cannot use Tor:]
-   [Appendix H: Windows Cleaning Tools]
-   [Appendix I: Using ShredOS to securely wipe an HDD drive:]
    -   [Windows:][11]
    -   [Linux:]
-   [Appendix J: Manufacturer tools for Wiping HDD and SSD drives:]
    -   [Tools that provide a boot disk for wiping from boot:]
    -   [Tools that provide only support from running OS (for external drives).]
-   [Appendix K: Considerations
