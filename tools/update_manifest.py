#!/usr/bin/env python3
"""
Update manifest.json after converting content files.
Run this after convert_yet.py or convert_songs.py to keep the manifest current.

Usage:
    python tools/update_manifest.py
"""

import json
import os
from datetime import date


def get_size_kb(path):
    if os.path.exists(path):
        return os.path.getsize(path) // 1024
    return 0


def count_songs(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return len(data.get('songs', []))


def count_verses(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return sum(
        len(ch['verses'])
        for b in data.get('books', [])
        for ch in b.get('chapters', [])
    )


def main():
    manifest_path = 'manifest.json'

    if not os.path.exists(manifest_path):
        print(f"Error: {manifest_path} not found. Run from repo root.")
        return

    with open(manifest_path, encoding='utf-8') as f:
        manifest = json.load(f)

    # Update date
    manifest['updated'] = str(date.today())

    # Update bible entries
    for bible in manifest.get('bibles', []):
        path = bible.get('filename', '')
        if os.path.exists(path):
            new_size = get_size_kb(path)
            if new_size != bible.get('size_kb', 0):
                bible['version'] = bible.get('version', 1) + 1
                bible['size_kb'] = new_size
                verses = count_verses(path)
                bible['verses'] = verses
                print(f"  Updated {bible['id']}: v{bible['version']}, {new_size} KB, {verses:,} verses")
            else:
                print(f"  {bible['id']}: unchanged")

    # Update song book entries
    for book in manifest.get('songs', []):
        path = book.get('filename', '')
        if os.path.exists(path):
            count = count_songs(path)
            if count != book.get('count', 0):
                book['version'] = book.get('version', 1) + 1
                book['count'] = count
                print(f"  Updated {book['id']}: v{book['version']}, {count} songs")
            else:
                print(f"  {book['id']}: unchanged ({count} songs)")

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nManifest updated: {manifest_path}")


if __name__ == "__main__":
    main()
