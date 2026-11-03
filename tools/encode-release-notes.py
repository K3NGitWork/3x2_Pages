#!/usr/bin/env python3
"""Encode's release notes (Mac only, download only): encode/release-notes/releases.json is the
list, this script writes it into encode/release-notes/index.html (between the
<!-- releases:mac --> markers), and points every Encode download link on the site at the newest
DMG. scripts/release-direct.sh in the Encode repo runs it for every release. A copy of
tools/release-notes.py (Unfold's), kept separate so the two apps never touch each other's pages.

  tools/encode-release-notes.py add --platform mac --version 1.0.1 --dmg Encode_1.0.1_2.dmg --notes "…"
  tools/encode-release-notes.py render                                     (rewrite the page from the JSON)
  tools/encode-release-notes.py html --notes "…"                           (the notes as HTML, for the appcast)

Adding a version that is already listed adds its "where" chips and replaces its date and, if
given, its notes. Notes are short lines: an intro sentence, then "New:", "Changed:" or "Fixed:"
followed by "- " items. **bold** for app labels, `code` for file names. Never mention Ko-fi.
"""
import argparse
import datetime
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIR = ROOT / "encode" / "release-notes"
DATA = DIR / "releases.json"
PAGE = DIR / "index.html"
DMG = "https://github.com/K3NGitWork/3x2_Pages/releases/download/encode-{v}/{dmg}"
# Any download link on the site: the "latest" alias or a versioned asset.
DMG_LINK = re.compile(r"https://github\.com/K3NGitWork/3x2_Pages/releases/"
                      r"(?:latest/download|download/encode-[0-9.]+)/Encode[^\"/]*\.dmg")
GROUPS = ("New", "Changed", "Fixed")
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")


def today():
    d = datetime.date.today()
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)


def parse_notes(text):
    """'Intro\\nNew:\\n- a\\n- b' → {"intro": "Intro", "New": ["a", "b"]}."""
    if re.search(r"ko-?fi", text, re.I):
        raise SystemExit("Release notes never mention Ko-fi. Leave that line out.")
    notes, group = {}, None
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.rstrip(":") in GROUPS and line.endswith(":"):
            group = line[:-1]
        elif line.startswith("- ") and group:
            notes.setdefault(group, []).append(line[2:].strip())
        else:
            notes["intro"] = (notes.get("intro", "") + " " + line).strip()
    return notes


def notes_html(notes):
    out = []
    if notes.get("intro"):
        out.append(f"<p>{inline(notes['intro'])}</p>")
    for group in GROUPS:
        if notes.get(group):
            items = "".join(f"<li>{inline(i)}</li>" for i in notes[group])
            out.append(f'<div class="w-release__group"><h3>{group}</h3><ul class="w-list">{items}</ul></div>')
    return "".join(out)


def entry_html(platform, release, latest):
    v = release["version"]
    badge = '<span class="w-latest">Latest</span>' if latest else ""
    where = "".join(f'<span class="w-where">{html.escape(w)}</span>' for w in release["where"])
    more = ""
    if platform == "mac" and release["where"] == ["Download"]:
        more = (f'<a class="w-more w-release__more" href="{dmg_url(release)}">Download {v}'
                '<svg class="w-sym" aria-hidden="true"><use href="../../assets/icons.svg#chevron_right"/></svg></a>')
    return (f'<article class="w-release" id="{platform}-{v}"><div>'
            f'<h2 class="w-release__version">{v}{badge}</h2>'
            f'<p class="w-release__date">{html.escape(release["date"])}</p>'
            f'<div class="w-release__where">{where}</div></div>'
            f'<div class="w-release__notes">{notes_html(release["notes"])}{more}</div></article>')


def dmg_url(release):
    return DMG.format(v=release["version"], dmg=release.get("dmg", "Encode.dmg"))


def point_downloads(data):
    """Every download link on the site → the newest Mac release that is a download."""
    latest = max((r for r in data["mac"] if "Download" in r["where"]), key=key)
    url = dmg_url(latest)
    # Encode's pages only: Unfold's are never touched.
    for page in (ROOT / "encode").rglob("*.html"):
        text = page.read_text()
        new = DMG_LINK.sub(url, text)
        if new != text:
            page.write_text(new)


def key(release):
    return tuple(int(p) for p in release["version"].split("."))


def render(data):
    point_downloads(data)
    page = PAGE.read_text()
    for platform in ("mac",):
        releases = sorted(data[platform], key=key, reverse=True)
        body = "\n".join(entry_html(platform, r, i == 0) for i, r in enumerate(releases))
        page, n = re.subn(rf"(<!-- releases:{platform} -->).*?(<!-- /releases:{platform} -->)",
                          lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", page, flags=re.S)
        assert n == 1, f"markers for {platform} missing in {PAGE}"
    PAGE.write_text(page)


def add(data, args):
    releases = data[args.platform]
    release = next((r for r in releases if r["version"] == args.version), None)
    if release is None:
        release = {"version": args.version, "date": "", "where": [], "notes": {}}
        releases.append(release)
    for w in args.where or []:
        if w not in release["where"]:
            release["where"].append(w)
    if not release["where"]:
        release["where"] = ["iOS App Store"] if args.platform == "ios" else ["Download"]
    release["date"] = args.status or args.date or today()
    if args.dmg:
        release["dmg"] = args.dmg
    if args.notes:
        release["notes"] = parse_notes(args.notes)
    elif not release["notes"]:
        raise SystemExit(f"{args.platform} {args.version} is new: give it --notes.")
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--platform", choices=("mac",), default="mac")
    a.add_argument("--version", required=True)
    a.add_argument("--where", action="append", help='"Download" (the default)')
    a.add_argument("--date", help='e.g. "22 October 2026"; default today')
    a.add_argument("--status", help='shown instead of a date while not live, e.g. "Submitted 19 October 2026"')
    a.add_argument("--notes")
    a.add_argument("--dmg", help='the DMG\'s file name in the GitHub release, e.g. "Encode_1.0.1_2.dmg"')
    sub.add_parser("render")
    h = sub.add_parser("html")
    h.add_argument("--notes", required=True)
    args = p.parse_args()

    if args.cmd == "html":
        print(notes_html(parse_notes(args.notes)))
        return
    data = json.loads(DATA.read_text())
    if args.cmd == "add":
        add(data, args)
    render(data)


if __name__ == "__main__":
    main()
