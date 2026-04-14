#!/usr/bin/env python3
"""
One-command workflow: convert/download content and push to GitHub.

Usage:
    python tools/publish.py --all-bibles          # Download all public domain Bibles
    python tools/publish.py --bible WEB           # Download one Bible from internet
    python tools/publish.py --yet path/to/file.yet  # Convert local .yet file
    python tools/publish.py --songs path/to/songs.txt --id RRZ --name "..." --language "..."
    python tools/publish.py --manifest-only       # Just update manifest and push
"""

import argparse, os, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))


def git_push(message):
    print(f"\nPushing: '{message}'")
    try:
        subprocess.run(['git', 'add', '-A'], check=True)
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'],
                                capture_output=True)
        if result.returncode == 0:
            print("  No changes to push.")
            return True
        subprocess.run(['git', 'commit', '-m', message], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("  Pushed ✓")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Git error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--all-bibles', action='store_true',
                        help='Download all public domain Bibles from internet')
    parser.add_argument('--bible', help='Download specific Bible by ID (WEB, ASV, etc.)')
    parser.add_argument('--yet', help='Convert a local .yet Bible file')
    parser.add_argument('--songs', help='Convert a local .txt song book file')
    parser.add_argument('--id', help='Song book ID')
    parser.add_argument('--name', help='Song book display name')
    parser.add_argument('--language', help='Song book language')
    parser.add_argument('--manifest-only', action='store_true')
    parser.add_argument('--no-push', action='store_true')
    args = parser.parse_args()

    commit_parts = []

    # Download from internet
    if args.all_bibles or args.bible:
        from download_bibles import download_translation, TRANSLATIONS, update_manifest
        if args.all_bibles:
            to_dl = TRANSLATIONS
        else:
            to_dl = [t for t in TRANSLATIONS
                     if t['id'].upper() == args.bible.upper()]
            if not to_dl:
                print(f"Unknown Bible ID: {args.bible}")
                sys.exit(1)

        downloaded = []
        for meta in to_dl:
            path, size_kb, verses = download_translation(meta)
            if path:
                downloaded.append((meta, size_kb))
                commit_parts.append(f"Add {meta['id']} ({verses:,} verses)")
        if downloaded:
            update_manifest(downloaded)

    # Convert local .yet file
    if args.yet:
        from convert_yet import convert as convert_yet
        out, bid, total = convert_yet(args.yet)
        commit_parts.append(f"Update {bid} Bible ({total:,} verses)")

    # Convert local song book
    if args.songs:
        from convert_songs import convert as convert_songs
        out, sid, count = convert_songs(
            args.songs, args.id, args.name, args.language)
        commit_parts.append(f"Update {sid} songs ({count} songs)")

    # Update manifest
    from update_manifest import main as update_manifest_main
    print("\nUpdating manifest...")
    update_manifest_main()

    if not commit_parts:
        commit_parts.append("Update content")

    if not args.no_push:
        git_push('; '.join(commit_parts))

    print("\nDone! App users get updates on next launch.")


if __name__ == '__main__':
    main()
