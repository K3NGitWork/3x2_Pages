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

Plain HTML and one stylesheet (`assets/style.css`, light and dark mode); no build step. The look
follows the Unfold Web design system; icons are Material Symbols Rounded (Apache 2.0) in
`assets/icons.svg`. Sources of the texts: `design/appstore_brief/` in the Unfold repository.

**Release notes:** `unfold/release-notes/releases.json` is the list; `tools/release-notes.py`
adds a version and rewrites the page (run it with `--help`). `scripts/release-direct.sh` in the
Unfold repo runs it for every download release; App Store versions are added by hand (see
`Distribution/AppStore/README.md` there).

**App Store link:** the pages use the placeholder `APP_STORE_URL`. Once the app is live, replace
it everywhere: `grep -rl APP_STORE_URL --include=*.html . | xargs sed -i '' 's#APP_STORE_URL#https://apps.apple.com/app/id…#g'`.
