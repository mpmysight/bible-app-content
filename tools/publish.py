#!/usr/bin/env python3
"""
One-command workflow: convert your source files and push to GitHub.

Usage:
    # Convert and push everything
    python tools/publish.py --all

    # Convert and push a specific Bible
    python tools/publish.py --bible path/to/bible.yet

    # Convert and push a specific song book
    python tools/publish.py --songs path/to/songs.txt --id RRZ --name "Runyankole Rukiga, Zaburi" --language Runyankole

    # Just update manifest and push (after manual file changes)
    python tools/publish.py --manifest-only
"""

import argparse
import os
import subprocess
import sys

# Add tools dir to path so we can import converters
sys.path.insert(0, os.path.dirname(__file__))
from convert_yet import convert as convert_yet
from convert_songs import convert as convert_songs
from update_manifest import main as update_manifest


def git_push(message):
    print(f"\nPushing to GitHub: '{message}'")
    try:
        subprocess.run(['git', 'add', '-A'], check=True)
        result = subprocess.run(
            ['git', 'diff', '--cached', '--quiet'],
            capture_output=True
        )
        if result.returncode == 0:
            print("  No changes to push.")
            return True
        subprocess.run(['git', 'commit', '-m', message], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("  Pushed successfully ✓")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Git error: {e}")
        print("  Make sure you have git configured and push access to the repo.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Convert content files and publish to GitHub')
    parser.add_argument('--bible', help='Path to .yet Bible file to convert')
    parser.add_argument('--songs', help='Path to song book .txt file to convert')
    parser.add_argument('--id', help='Song book ID (used with --songs)')
    parser.add_argument('--name', help='Song book name (used with --songs)')
    parser.add_argument('--language', help='Language (used with --songs)')
    parser.add_argument('--all', action='store_true',
                        help='Just update manifest and push all changes')
    parser.add_argument('--manifest-only', action='store_true',
                        help='Only update manifest.json and push')
    parser.add_argument('--no-push', action='store_true',
                        help='Convert only, do not push to GitHub')
    args = parser.parse_args()

    changed_files = []
    commit_parts = []

    # Convert Bible
    if args.bible:
        if not os.path.exists(args.bible):
            print(f"Error: File not found: {args.bible}")
            sys.exit(1)
        print("\n=== Converting Bible ===")
        out, bid, total = convert_yet(args.bible)
        changed_files.append(out)
        commit_parts.append(f"Update {bid} Bible ({total:,} verses)")

    # Convert Songs
    if args.songs:
        if not os.path.exists(args.songs):
            print(f"Error: File not found: {args.songs}")
            sys.exit(1)
        print("\n=== Converting Song Book ===")
        out, sid, count = convert_songs(
            args.songs, args.id, args.name, args.language)
        changed_files.append(out)
        commit_parts.append(f"Update {sid} songs ({count} songs)")

    # Update manifest
    print("\n=== Updating Manifest ===")
    update_manifest()
    changed_files.append('manifest.json')

    if not commit_parts:
        commit_parts.append("Update content")

    commit_msg = "; ".join(commit_parts)

    if args.no_push:
        print(f"\nFiles ready (--no-push specified, skipping git push):")
        for f in changed_files:
            print(f"  {f}")
    else:
        git_push(commit_msg)

    print("\nDone!")
    print("The app will pick up changes on next launch when online.")


if __name__ == "__main__":
    main()
