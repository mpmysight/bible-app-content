# Twino Bible — Content Repository

This repository hosts Bible translations, song books, and devotional content
for the Twino Bible app. The app fetches content from here on demand.

## Repository Structure

```
bible-app-content/
├── bibles/
│   ├── rr64.json          Baibuli Erikwera — Runyankole (1964)
│   ├── web.json           World English Bible
│   ├── asv.json           American Standard Version
│   ├── darby.json         Darby Bible
│   └── ylt.json           Young's Literal Translation
├── songs/
│   ├── songs_en.json      English Hymns (69 public domain hymns)
│   └── songs_rrz.json     Runyankole Rukiga, Zaburi (315 songs)
├── devotions/
│   └── devotions.json     Morning & Evening (Spurgeon, bundled in app)
├── manifest.json          Master catalog — app reads this first
└── tools/
    ├── download_bibles.py  Download public domain Bibles from internet
    ├── convert_yet.py      Convert .yet Bible files to JSON
    ├── convert_songs.py    Convert song book .txt files to JSON
    ├── update_manifest.py  Refresh manifest.json
    └── publish.py          One-command convert + push
```

## How to Add Content

### Download public domain Bibles (WEB, ASV, Darby, YLT, BBE)

```bash
# Download all at once
python tools/publish.py --all-bibles

# Or one at a time
python tools/publish.py --bible WEB
python tools/publish.py --bible ASV
```

### Convert your own .yet Bible file

```bash
python tools/publish.py --yet path/to/Runyankore_RR64.yet
```

### Add a song book

```bash
python tools/publish.py --songs path/to/_rrz.txt \
  --id RRZ --name "Runyankole Rukiga, Zaburi" --language Runyankole
```

### Just update manifest and push

```bash
python tools/publish.py --manifest-only
```

## Adding New Content to the Catalog

To add a new Bible or song book to the app's download catalog:

1. Add the JSON file to `bibles/` or `songs/`
2. Add an entry to `manifest.json` under `"bibles"` or `"songs"`
3. For song books set `"category": "african"` or `"category": "international"`
4. Run `python tools/publish.py --manifest-only` to push

### Song Book Entry Format

```json
{
  "id": "XYZ",
  "name": "My Song Book",
  "language": "English",
  "region": "Africa",
  "category": "african",
  "filename": "songs/songs_xyz.json",
  "version": 1,
  "count": 150,
  "bundled": false,
  "description": "Brief description of the song book."
}
```

### Bible Entry Format

```json
{
  "id": "WEB",
  "shortName": "WEB",
  "longName": "World English Bible",
  "language": "English",
  "region": "International",
  "filename": "bibles/web.json",
  "version": 1,
  "size_kb": 4800,
  "bundled": false,
  "description": "Modern English translation. Public domain."
}
```

## Content URLs (raw GitHub)

The app fetches from:
```
https://raw.githubusercontent.com/mpmysight/bible-app-content/main/manifest.json
https://raw.githubusercontent.com/mpmysight/bible-app-content/main/bibles/rr64.json
https://raw.githubusercontent.com/mpmysight/bible-app-content/main/songs/songs_rrz.json
```
