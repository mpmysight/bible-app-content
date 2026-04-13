#!/usr/bin/env python3
"""
Convert an androidbible song book .txt file to the app's JSON format.

Usage:
    python tools/convert_songs.py mysongs.txt
    python tools/convert_songs.py mysongs.txt --id RRZ --name "My Song Book" --output songs/rrz.json

Song book format (from Alkitab Developer Guide):
    code 1
    title Song Title
    authors_lyric Author Name
    *1
    Verse 1 lyrics...
    *ref
    Chorus lyrics...
    *2
    Verse 2 lyrics...
    ===
"""

import json
import os
import re
import sys
import argparse


def clean_text(text):
    """Remove <u></u> underline markup used for syllable emphasis."""
    return re.sub(r'</?u>', '', text).strip()


def parse_songs(filepath):
    songs = []
    current = {}
    current_section = None
    sections = {}

    def save():
        if not current.get('code'):
            return
        song = {
            'id': int(current['code']) if current['code'].isdigit() else len(songs) + 1,
            'number': str(current['code']),
            'title': current.get('title', '').strip(),
            'author': (
                current.get('authors_lyric') or
                current.get('authors_music') or
                None
            ),
            'key': current.get('key', None),
            'verses': [],
            'chorus': None,
        }
        for k in sorted(sections.keys(), key=lambda x: (x == 'ref', x)):
            text = clean_text(sections[k].strip())
            if not text:
                continue
            if k == 'ref':
                song['chorus'] = text
            else:
                song['verses'].append(text)
        if song['verses'] or song['chorus']:
            songs.append(song)

    with open(filepath, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n\r')

            if line.strip() == '===':
                save()
                current = {}
                current_section = None
                sections = {}
                continue

            if line.startswith('*'):
                key = line[1:].strip()
                current_section = key
                sections[current_section] = ''
                continue

            if current_section is None:
                # Parse metadata fields
                if line.startswith('code '):
                    current['code'] = line[5:].strip()
                elif line.startswith('title '):
                    current['title'] = line[6:].strip()
                elif line.startswith('title_original '):
                    current['title_original'] = line[15:].strip()
                elif line.startswith('authors_lyric '):
                    current['authors_lyric'] = line[14:].strip()
                elif line.startswith('authors_music '):
                    current['authors_music'] = line[14:].strip()
                elif line.startswith('1='):
                    current['key'] = line.strip()
                elif line.startswith('tune '):
                    current['tune'] = line[5:].strip()
                continue

            # Append to current section
            if current_section is not None:
                if sections[current_section]:
                    sections[current_section] += '\n'
                sections[current_section] += line

    # Save last song (file may not end with ===)
    save()
    return songs


def convert(input_path, book_id=None, book_name=None, language=None, output_path=None):
    print(f"Reading {input_path} ...")

    songs = parse_songs(input_path)

    if not book_id:
        book_id = os.path.splitext(os.path.basename(input_path))[0].upper()
        book_id = book_id.lstrip('_')  # remove leading underscore if present
    if not book_name:
        book_name = book_id
    if not language:
        language = 'Unknown'

    result = {
        "id": book_id,
        "name": book_name,
        "language": language,
        "songs": songs,
    }

    print(f"  Song book: {book_id} — {book_name}")
    print(f"  Songs parsed: {len(songs)}")
    if songs:
        print(f"  First song: {songs[0]['title']}")
        print(f"  Last song:  {songs[-1]['title']}")

    if output_path is None:
        output_path = os.path.join("songs", f"songs_{book_id.lower()}.json")

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(output_path) // 1024
    print(f"  Saved: {output_path} ({size_kb:,} KB) ✓")
    return output_path, book_id, len(songs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert song book .txt to app JSON")
    parser.add_argument("input", help="Input .txt song book file")
    parser.add_argument("--id", help="Song book ID (e.g. RRZ, EN)")
    parser.add_argument("--name", help="Song book display name")
    parser.add_argument("--language", help="Language (e.g. Runyankole, English)")
    parser.add_argument("--output", help="Output JSON path (default: songs/songs_<id>.json)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    convert(args.input, args.id, args.name, args.language, args.output)
    print("\nDone! Push the output file to your GitHub content repo.")
