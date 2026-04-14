#!/usr/bin/env python3
"""
Update manifest.json after converting/downloading content.
Run from repo root: python tools/update_manifest.py
"""
import json, os
from datetime import date


def get_size_kb(path):
    return os.path.getsize(path) // 1024 if os.path.exists(path) else 0


def count_songs(path):
    if not os.path.exists(path): return 0
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return len(data.get('songs', []))


def count_verses(path):
    if not os.path.exists(path): return 0
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

    manifest['updated'] = str(date.today())

    for bible in manifest.get('bibles', []):
        path = bible.get('filename', '')
        if os.path.exists(path):
            new_size = get_size_kb(path)
            old_size = bible.get('size_kb', 0)
            if new_size != old_size:
                bible['version'] = bible.get('version', 1) + 1
                bible['size_kb'] = new_size
                bible['verses'] = count_verses(path)
                print(f"  Updated {bible['id']}: v{bible['version']}, "
                      f"{new_size}KB, {bible['verses']:,} verses")
            else:
                print(f"  {bible['id']}: unchanged")

    for book in manifest.get('songs', []):
        path = book.get('filename', '')
        if os.path.exists(path):
            count = count_songs(path)
            old_count = book.get('count', 0)
            if count != old_count:
                book['version'] = book.get('version', 1) + 1
                book['count'] = count
                print(f"  Updated {book['id']}: v{book['version']}, {count} songs")
            else:
                print(f"  {book['id']}: unchanged ({count} songs)")

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nmanifest.json saved (updated: {manifest['updated']})")


if __name__ == '__main__':
    main()
