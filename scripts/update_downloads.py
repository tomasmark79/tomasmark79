#!/usr/bin/env python3
"""Refresh GNOME extension download labels without changing README formatting."""

import argparse
import json
from pathlib import Path
import re
from urllib.request import urlopen


LABEL = re.compile(
    r"\[\d+\]\((https://extensions\.gnome\.org/extension/(\d+)/[^)]+)\)"
)


def fetch_downloads(extension_id):
    url = f"https://extensions.gnome.org/extension-info/?pk={extension_id}"
    with urlopen(url, timeout=30) as response:
        data = json.load(response)
    count = data.get("downloads")
    if data.get("pk") != int(extension_id) or type(count) is not int or count < 0:
        raise ValueError(f"Invalid download count for extension {extension_id}")
    return count


def update_readme(text, fetch=fetch_downloads):
    if not LABEL.search(text):
        raise ValueError("No GNOME download labels found in README")

    def replace(match):
        return f"[{fetch(match[2])}]({match[1]})"

    return LABEL.sub(replace, text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=Path("README.md"))
    args = parser.parse_args()
    original = args.readme.read_text(encoding="utf-8")
    updated = update_readme(original)
    # Fetch and validate every count before writing anything.
    if updated != original:
        args.readme.write_text(updated, encoding="utf-8")
        print("Updated GNOME extension download counts")
    else:
        print("GNOME extension download counts are current")


if __name__ == "__main__":
    main()
