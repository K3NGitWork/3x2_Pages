# 3x2_Pages

Public web pages for 3x2 Studio's apps, served with GitHub Pages.

| Path | Page |
| --- | --- |
| `/` | 3x2 Studio |
| `/unfold/` | Unfold overview |
| `/unfold/help/` | Unfold guide (opened from the app) |
| `/unfold/release-notes/` | Unfold release notes, Mac and iPhone & iPad |
| `/unfold/support/` | Unfold support (App Store "Support URL") |
| `/unfold/privacy/` | Unfold privacy policy (App Store "Privacy Policy URL") |
| `/encode/` | Encode overview |
| `/encode/support/` | Encode support |
| `/encode/release-notes/` | Encode release notes (Mac) |
| `/encode/privacy/` | Encode privacy policy |
| `/encode/licenses/` | Encode's libraries, their licenses and the GPL source download |

Plain HTML and one stylesheet (`assets/style.css`, light and dark mode); no build step. The look
follows the Unfold Web design system; Encode's pages add `class="theme-encode"` on `<html>`, which
swaps the accent and icon colors (Encode Web design system, in the Encode repo's `docs/web-design/`); icons are Material Symbols Rounded (Apache 2.0) in
`assets/icons.svg`. Sources of the texts: `design/appstore_brief/` in the Unfold repository.

**Release notes:** `unfold/release-notes/releases.json` is the list; `tools/release-notes.py`
adds a version, rewrites the page and points every download link at the newest DMG (run it with `--help`). `scripts/release-direct.sh` in the
Unfold repo runs it for every download release; App Store versions are added by hand (see
`Distribution/AppStore/README.md` there).

**App Store links:** one app record serves Mac and iPhone/iPad (Apple ID 6822054531):
`https://apps.apple.com/app/id6822054531` for iOS, with `?platform=mac` for the Mac App Store.
They only open once the app is live.

**Search engines:** every page has a description, a canonical URL and Open Graph tags (shared
links show `assets/social.jpg`); the Unfold page adds schema.org `SoftwareApplication` data and
Safari's App Store banner. `sitemap.xml` lists the pages: submit
`https://k3ngitwork.github.io/3x2_Pages/sitemap.xml` once in Google Search Console and Bing
Webmaster Tools. (A `robots.txt` only counts at the domain root, which a project page can't serve.)

**Encode:** `encode/release-notes/releases.json` and `tools/encode-release-notes.py` work like
Unfold's, for Encode's pages only; `encode/appcast.xml` is its update feed. The DMG and the GPL
source tarballs (x265, FFmpeg) are assets of the GitHub release `encode-<version>`.
