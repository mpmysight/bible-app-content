#!/usr/bin/env python3
"""
Convert a .yet Bible file to the app's JSON format.

Usage:
    python tools/convert_yet.py input.yet
    python tools/convert_yet.py input.yet --output bibles/custom.json

The .yet format is tab-separated text used by the androidbible project.
Each verse line: verse [TAB] book_1 [TAB] chapter_1 [TAB] verse_1 [TAB] text
"""

import json
import os
import sys
import argparse


def convert(input_path, output_path=None):
    print(f"Reading {input_path} ...")

    translation_id = None
    long_name = None
    book_names = {}
    book_abbreviations = {}
    verses = {}

    with open(input_path, encoding='utf-8', errors='replace') as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip('\n\r')
            if not line or line.lstrip().startswith('#'):
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue

            command = parts[0]

            if command == 'info':
                if len(parts) >= 3:
                    key, value = parts[1], parts[2]
                    if key == 'shortName':
                        translation_id = value.strip()
                    elif key == 'longName':
                        long_name = value.strip()

            elif command == 'book_name':
                if len(parts) >= 3:
                    book_1 = int(parts[1])
                    name = parts[2]
                    abbr = parts[3] if len(parts) > 3 and parts[3].strip() else name[:4]
                    book_names[book_1] = name
                    book_abbreviations[book_1] = abbr.strip()

            elif command == 'verse':
                if len(parts) >= 5:
                    book_1 = int(parts[1])
                    chapter_1 = int(parts[2])
                    verse_1 = int(parts[3])
                    text = parts[4]
                    if book_1 not in verses:
                        verses[book_1] = {}
                    if chapter_1 not in verses[book_1]:
                        verses[book_1][chapter_1] = []
                    verses[book_1][chapter_1].append({
                        "verse": verse_1,
                        "text": text,
                    })

    if not translation_id:
        translation_id = os.path.splitext(os.path.basename(input_path))[0].upper()
    if not long_name:
        long_name = translation_id

    print(f"  Translation: {translation_id} — {long_name}")
    print(f"  Books: {len(verses)}")

    books_output = []
    for book_1 in sorted(verses.keys()):
        chapters_output = [
            {"chapter": ch, "verses": verses[book_1][ch]}
            for ch in sorted(verses[book_1].keys())
        ]
        books_output.append({
            "bookId": book_1 - 1,
            "name": book_names.get(book_1, f"Book {book_1}"),
            "abbreviation": book_abbreviations.get(book_1, f"B{book_1}"),
            "chapters": chapters_output,
        })

    result = {
        "translation": translation_id,
        "longName": long_name,
        "books": books_output,
    }

    total = sum(
        len(ch["verses"])
        for b in books_output
        for ch in b["chapters"]
    )
    print(f"  Verses: {total:,}")

    if output_path is None:
        output_path = os.path.join("bibles", f"{translation_id.lower()}.json")

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(output_path) // 1024
    print(f"  Saved: {output_path} ({size_kb:,} KB) ✓")
    return output_path, translation_id, total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert .yet Bible to app JSON")
    parser.add_argument("input", help="Input .yet file path")
    parser.add_argument("--output", help="Output JSON path (default: bibles/<id>.json)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    convert(args.input, args.output)
    print("\nDone! Push the output file to your GitHub content repo.")
