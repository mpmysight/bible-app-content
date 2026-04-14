#!/usr/bin/env python3
"""
Download public domain Bible translations and convert to app JSON format.
Run this from the bible-app-content directory.

Usage:
    python tools/download_bibles.py              # Download all
    python tools/download_bibles.py --id WEB     # Download specific one
    python tools/download_bibles.py --list        # Show available

Sources:
  - scrollmapper/bible_databases on GitHub (JSDelivr CDN)
  - All translations are public domain
"""

import json
import os
import sys
import argparse
import urllib.request

TRANSLATIONS = [
    {
        'id': 'WEB',
        'shortName': 'WEB',
        'longName': 'World English Bible',
        'language': 'English',
        'region': 'International',
        'source_id': 'web',  # scrollmapper ID
    },
    {
        'id': 'ASV',
        'shortName': 'ASV',
        'longName': 'American Standard Version',
        'language': 'English',
        'region': 'International',
        'source_id': 'asv',
    },
    {
        'id': 'DARBY',
        'shortName': 'DARBY',
        'longName': 'Darby Bible',
        'language': 'English',
        'region': 'International',
        'source_id': 'darby',
    },
    {
        'id': 'YLT',
        'shortName': 'YLT',
        'longName': "Young's Literal Translation",
        'language': 'English',
        'region': 'International',
        'source_id': 'ylt',
    },
    {
        'id': 'BBE',
        'shortName': 'BBE',
        'longName': 'Bible in Basic English',
        'language': 'English',
        'region': 'International',
        'source_id': 'bbe',
    },
]

# scrollmapper book order (1-based) maps to our 0-based bookId
# Their books array index = our bookId
BOOK_COUNT = 66

def fetch_scrollmapper(source_id):
    """Fetch Bible JSON from scrollmapper via JSDelivr CDN"""
    url = f'https://cdn.jsdelivr.net/gh/scrollmapper/bible_databases@master/json/t_{source_id}.json'
    print(f"  Fetching from {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def convert_scrollmapper(data, meta):
    """Convert scrollmapper format to our app format"""
    # scrollmapper format:
    # { "resultset": { "row": [ {"field": [book_nr, chapter, verse, text]}, ... ] } }
    
    books_data = {}  # book_nr -> {chapter -> [verses]}
    
    rows = data.get('resultset', {}).get('row', [])
    for row in rows:
        fields = row.get('field', [])
        if len(fields) < 4:
            continue
        book_nr = int(fields[0])   # 1-based
        chapter = int(fields[1])
        verse_nr = int(fields[2])
        text = str(fields[3]).strip()
        
        if book_nr not in books_data:
            books_data[book_nr] = {}
        if chapter not in books_data[book_nr]:
            books_data[book_nr][chapter] = []
        books_data[book_nr][chapter].append({
            'verse': verse_nr,
            'text': text,
        })
    
    books_output = []
    for book_nr in sorted(books_data.keys()):
        book_id = book_nr - 1  # 0-based
        chapters_output = [
            {'chapter': ch, 'verses': books_data[book_nr][ch]}
            for ch in sorted(books_data[book_nr].keys())
        ]
        books_output.append({
            'bookId': book_id,
            'name': get_book_name(book_id),
            'abbreviation': get_book_abbr(book_id),
            'chapters': chapters_output,
        })
    
    return {
        'translation': meta['id'],
        'longName': meta['longName'],
        'language': meta['language'],
        'books': books_output,
    }


def get_book_name(book_id):
    names = [
        'Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges',
        'Ruth','1 Samuel','2 Samuel','1 Kings','2 Kings','1 Chronicles','2 Chronicles',
        'Ezra','Nehemiah','Esther','Job','Psalms','Proverbs','Ecclesiastes',
        'Song of Solomon','Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel',
        'Hosea','Joel','Amos','Obadiah','Jonah','Micah','Nahum','Habakkuk',
        'Zephaniah','Haggai','Zechariah','Malachi','Matthew','Mark','Luke','John',
        'Acts','Romans','1 Corinthians','2 Corinthians','Galatians','Ephesians',
        'Philippians','Colossians','1 Thessalonians','2 Thessalonians','1 Timothy',
        '2 Timothy','Titus','Philemon','Hebrews','James','1 Peter','2 Peter',
        '1 John','2 John','3 John','Jude','Revelation',
    ]
    return names[book_id] if book_id < len(names) else f'Book {book_id+1}'


def get_book_abbr(book_id):
    abbrs = [
        'Gen','Exo','Lev','Num','Deu','Josh','Judg','Ruth','1Sam','2Sam',
        '1Kin','2Kin','1Chr','2Chr','Ezr','Neh','Esth','Job','Ps','Prov',
        'Eccl','Song','Isa','Jer','Lam','Ezek','Dan','Hos','Joel','Am',
        'Oba','Jona','Mic','Nah','Hab','Zeph','Hag','Zech','Mal',
        'Matt','Mark','Luke','John','Acts','Rom','1Cor','2Cor','Gal','Eph',
        'Phil','Col','1Ths','2Ths','1Tim','2Tim','Tit','Phlm','Heb','Jam',
        '1Pet','2Pet','1Jn','2Jn','3Jn','Jud','Rev',
    ]
    return abbrs[book_id] if book_id < len(abbrs) else f'B{book_id+1}'


def download_translation(meta, output_dir='bibles'):
    print(f"\nDownloading {meta['id']} — {meta['longName']}")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        raw = fetch_scrollmapper(meta['source_id'])
        converted = convert_scrollmapper(raw, meta)
        
        total_verses = sum(
            len(ch['verses'])
            for b in converted['books']
            for ch in b['chapters']
        )
        print(f"  Books: {len(converted['books'])}, Verses: {total_verses:,}")
        
        out_path = os.path.join(output_dir, f"{meta['id'].lower()}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(converted, f, ensure_ascii=False, separators=(',', ':'))
        
        size_kb = os.path.getsize(out_path) // 1024
        print(f"  Saved: {out_path} ({size_kb:,} KB) ✓")
        return out_path, size_kb, total_verses
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None, 0, 0


def update_manifest(downloaded):
    """Update manifest.json with downloaded Bible info"""
    if not os.path.exists('manifest.json'):
        print("manifest.json not found — run from repo root")
        return
    
    with open('manifest.json') as f:
        manifest = json.load(f)
    
    for meta, size_kb in downloaded:
        # Find and update existing entry
        for bible in manifest.get('bibles', []):
            if bible['id'] == meta['id']:
                bible['size_kb'] = size_kb
                bible['version'] = bible.get('version', 0) + 1
                print(f"  Updated manifest for {meta['id']}")
                break
    
    with open('manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print("manifest.json updated")


def main():
    parser = argparse.ArgumentParser(description='Download public domain Bibles')
    parser.add_argument('--id', help='Download specific translation (e.g. WEB)')
    parser.add_argument('--list', action='store_true', help='List available translations')
    args = parser.parse_args()
    
    if args.list:
        print("\nAvailable translations:")
        for t in TRANSLATIONS:
            print(f"  {t['id']:8} {t['longName']} ({t['language']})")
        return
    
    to_download = TRANSLATIONS
    if args.id:
        to_download = [t for t in TRANSLATIONS if t['id'].upper() == args.id.upper()]
        if not to_download:
            print(f"Unknown ID: {args.id}")
            print(f"Available: {', '.join(t['id'] for t in TRANSLATIONS)}")
            sys.exit(1)
    
    print(f"Downloading {len(to_download)} translation(s)...")
    downloaded = []
    for meta in to_download:
        path, size_kb, verses = download_translation(meta)
        if path:
            downloaded.append((meta, size_kb))
    
    if downloaded:
        print(f"\nUpdating manifest...")
        update_manifest(downloaded)
        print(f"\nDone! Push to GitHub:")
        print(f"  git add bibles/ manifest.json")
        print(f"  git commit -m 'Add Bible translations'")
        print(f"  git push")


if __name__ == '__main__':
    main()
