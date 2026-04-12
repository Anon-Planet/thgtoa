Welcome.

**[IMPORTANT RECOMMENDATION FOR UKRAINIANS. ВАЖЛИВА РЕКОМЕНДАЦІЯ ДЛЯ УКРАЇНЦІВ](briar.html)**

This is a maintained guide with the aim of providing an introduction to various online tracking techniques, online ID verification techniques, and detailed guidance to creating and maintaining (truly) anonymous online identities. <span style="color: red">**It is written with hope for activists, journalists, scientists, lawyers, whistle-blowers, and good people being oppressed, censored, harassed anywhere!**</span> This guide has no affiliation with the [Anonymous](https://en.wikipedia.org/wiki/Anonymous_(hacker_group)) <sup>[[Wikiless]](https://wikiless.com/wiki/Anonymous_(hacker_group))</sup> <sup>[[Archive.org]](https://web.archive.org/web/https://en.wikipedia.org/wiki/Anonymous_(hacker_group))</sup> collective/movement.

This guide is an open-source non-profit initiative, [licensed](LICENSE.html) under **Creative Commons Attribution-NonCommercial 4.0 International** ([cc-by-nc-4.0](https://creativecommons.org/licenses/by-nc/4.0/) <sup>[[Archive.org]](https://web.archive.org/web/https://creativecommons.org/licenses/by-nc/4.0/)</sup>) and is **not sponsored/endorsed by any commercial/governmental entity**. This means that you are free to use our guide for pretty much any purpose **excluding commercially** as long as you do attribute it. There are no ads or any affiliate links.

**If you would like to make a donation to help this project, you can do so from [here](donations.html) where you will also find the project goals. All the donations will be strictly used within the context of this project. All donations and spendings are logged on the donations page.**

**Ways to read or export the guide**

- **In your browser:** [Hitchhiker's Guide](https://www.anonymousplanet.org/guide/) (hosted site). After a local build you can also open `site/guide/index.html` directly.
- **Local HTML preview:** from the repository root, with Python 3 and [MkDocs Material](https://squidfunk.github.io/mkdocs-material/getting-started/) installed (`pip install mkdocs-material`), run `mkdocs serve` and open the URL printed in the terminal (for example `http://127.0.0.1:8000`).
- **PDF (local build):** from the repository root, using the same environment, run:

  ```bash
  python scripts/build_guide_pdf.py
  ```

  This runs `mkdocs build` (output defaults to `./site`), then uses **Google Chrome** or **Microsoft Edge** in headless mode to print `site/guide/index.html` to **`export/guide.pdf`** (images and styling preserved). If the site is already built: `python scripts/build_guide_pdf.py --skip-mkdocs`. Other options: `--site-dir`, `--pdf`, and `python scripts/build_guide_pdf.py --help`.

  On **GitHub Actions**, the [Build guide PDF](https://github.com/Anon-Planet/thgtoa/actions/workflows/build-pdf.yml) workflow does the same using Chromium on Ubuntu when you push to `main` or open a pull request that touches the guide or build inputs; download the **`guide-pdf`** artifact from a successful run. You can also run it manually (**Actions** → **Build guide PDF** → **Run workflow**).
- **OpenDocument (ODT):** not produced by this repository (previous hosted export removed).
- **Raw Markdown (very large):** [docs/guide/index.md on GitHub](https://raw.githubusercontent.com/Anon-Planet/thgtoa/refs/heads/main/docs/guide/index.md)

**Mirrors:**
- <del>Hidden service: <http://thgtoa3jzy3doku7hkna32htpghjijefscwvh4dyjgfydbbjkeiohgid.onion/></del> **Host down**

Feel free to submit issues using Github Issues with the repository link above. Criticism, opinions, and ideas are welcome!

**Follow or contact us on:**

Discussion Channels:
- Matrix room: <https://matrix.to/#/#anonymity:anonymousplanet.net>
- Matrix space: <https://matrix.to/#/#psa:anonymousplanet.net>

Have a good read and feel free to share and/or recommend it!
