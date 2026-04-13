# Bible App Content Repository

This repository hosts Bible translations, song books, and devotional content
for the Bible App. The app fetches content from here on launch and caches it locally.

## Structure

```
bible-app-content/
├── bibles/
│   ├── kjv.json          King James Version
│   └── rr64.json         Baibuli Erikwera — Runyankole (1964)
├── songs/
│   ├── songs_en.json     English Hymns
│   └── songs_rrz.json    Runyankole Rukiga, Zaburi (315 songs)
├── devotions/
│   └── devotions.json    Offline devotions fallback
├── manifest.json         Content catalogue (app reads this first)
└── tools/                Conversion scripts (run locally, not deployed)
    ├── convert_yet.py    .yet Bible → JSON
    ├── convert_songs.py  Song book .txt → JSON
    ├── update_manifest.py Update manifest after converting
    └── publish.py        One-command convert + push
```

## How to Update Content

### Update the Runyankole Bible

1. Make corrections to your `.yet` source file
2. Run from this repo root:
```bash
python tools/publish.py --bible path/to/Runyankore_RR64.yet
```
This converts it, updates the manifest, and pushes to GitHub.
All app users get the update on their next launch.

### Update a Song Book

```bash
python tools/publish.py --songs path/to/_rrz.txt --id RRZ --name "Runyankole Rukiga, Zaburi" --language Runyankole
```

### Convert Only (no push)

```bash
python tools/convert_yet.py path/to/bible.yet
python tools/convert_songs.py path/to/songs.txt --id RRZ
```

### Push All Changes Manually

```bash
python tools/publish.py --manifest-only
```

## Adding a New Bible Translation

1. Get a `.yet` file for the translation
2. Run: `python tools/convert_yet.py translation.yet`
3. Add an entry to `manifest.json` under `"bibles"`
4. Run: `python tools/publish.py --manifest-only`

## Adding a New Song Book

1. Create a `.txt` file in the androidbible song book format
2. Run: `python tools/convert_songs.py mysongs.txt --id CODE --name "Book Name" --language Language`
3. Add an entry to `manifest.json` under `"songs"`
4. Run: `python tools/publish.py --manifest-only`

## How the App Uses This Repo

The app fetches:
```
https://raw.githubusercontent.com/[your-username]/bible-app-content/main/manifest.json
```

It compares version numbers in the manifest with its cached copies.
If the server version is newer, it downloads the updated file and caches it.
If offline, it uses the last cached version (or the bundled fallback).

## Content URLs (raw GitHub)

```
https://raw.githubusercontent.com/[your-username]/bible-app-content/main/bibles/rr64.json
https://raw.githubusercontent.com/[your-username]/bible-app-content/main/songs/songs_rrz.json
https://raw.githubusercontent.com/[your-username]/bible-app-content/main/manifest.json
```

Replace `[your-username]` with your GitHub username after creating the repo.
