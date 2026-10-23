#!/usr/bin/env python3
"""Unfold's release notes: unfold/release-notes/releases.json is the list, this script writes it
into unfold/release-notes/index.html (between the <!-- releases:mac --> and <!-- releases:ios -->
markers). scripts/release-direct.sh in the Unfold repo runs it for every download release.

  tools/release-notes.py add --platform mac --version 1.0.1 --where Download --notes "…"
  tools/release-notes.py add --platform mac --version 1.0.1 --where "Mac App Store"
  tools/release-notes.py add --platform ios --version 1.0.1 --where "iOS App Store" --status "Submitted 23 October 2026" --notes "…"
  tools/release-notes.py add --platform ios --version 1.0.1          (live: the status becomes today's date)
  tools/release-notes.py render                                     (rewrite the page from the JSON)
  tools/release-notes.py html --notes "…"                           (the notes as HTML, for the appcast)

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
DIR = ROOT / "unfold" / "release-notes"
DATA = DIR / "releases.json"
PAGE = DIR / "index.html"
DMG = "https://github.com/K3NGitWork/3x2_Pages/releases/download/unfold-{v}/Unfold.dmg"
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
        more = (f'<a class="w-more w-release__more" href="{DMG.format(v=v)}">Download {v}'
                '<svg class="w-sym" aria-hidden="true"><use href="../../assets/icons.svg#chevron_right"/></svg></a>')
    return (f'<article class="w-release" id="{platform}-{v}"><div>'
            f'<h2 class="w-release__version">{v}{badge}</h2>'
            f'<p class="w-release__date">{html.escape(release["date"])}</p>'
            f'<div class="w-release__where">{where}</div></div>'
            f'<div class="w-release__notes">{notes_html(release["notes"])}{more}</div></article>')


def key(release):
    return tuple(int(p) for p in release["version"].split("."))


def render(data):
    page = PAGE.read_text()
    for platform in ("mac", "ios"):
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
    if args.notes:
        release["notes"] = parse_notes(args.notes)
    elif not release["notes"]:
        raise SystemExit(f"{args.platform} {args.version} is new: give it --notes.")
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--platform", choices=("mac", "ios"), required=True)
    a.add_argument("--version", required=True)
    a.add_argument("--where", action="append", help='"Download", "Mac App Store" or "iOS App Store"')
    a.add_argument("--date", help='e.g. "22 October 2026"; default today')
    a.add_argument("--status", help='shown instead of a date while not live, e.g. "Submitted 19 October 2026"')
    a.add_argument("--notes")
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
