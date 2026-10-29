import argparse
import sys
from urllib.parse import urlsplit

import requests
from fastapi import HTTPException

from libs.databases.models.badge import Badge
from libs.databases.models.wallpaper import Wallpaper
from libs.storages.badge_uploads import BadgeUploads
from libs.storages.wallpaper_uploads import WallpaperUploads


def download(url, max_bytes):
    with requests.get(url, stream=True, timeout=(10, 30)) as response:
        response.raise_for_status()
        if urlsplit(response.url).scheme.lower() not in ("http", "https"):
            raise ValueError("Only HTTP/HTTPS images are supported")
        data = bytearray()
        for chunk in response.iter_content(chunk_size=65536):
            data.extend(chunk)
            if len(data) > max_bytes:
                raise ValueError("Image exceeds 8 MiB")
        return bytes(data)


def localize(records, uploads, label, dry_run=False):
    migrated = skipped = failed = 0
    for record in records:
        previous = record.url
        if not isinstance(previous, str) or urlsplit(previous).scheme.lower() not in ("http", "https"):
            skipped += 1
            continue
        if dry_run:
            print(f"Would migrate {label} #{record.id}")
            migrated += 1
            continue
        local_url = None
        try:
            data = download(previous, uploads.MAX_BYTES)
            # A record ID is a stable, positive namespace for these filenames.
            local_url = uploads.store(data, record.id)
            record.url = local_url
            record.saveOrFail()
        except Exception as error:
            record.url = previous
            if local_url is not None:
                uploads.delete(local_url)
            failed += 1
            detail = error.detail if isinstance(error, HTTPException) else str(error)
            print(f"Failed {label} #{record.id}: {detail}")
            continue
        migrated += 1
        print(f"Migrated {label} #{record.id}")
    action = "would migrate" if dry_run else "migrated"
    print(f"{label}: {migrated} {action}, {skipped} skipped, {failed} failed")
    return failed


def run():
    parser = argparse.ArgumentParser(
        prog="python3 bot.py localize-images",
        description="Download remote wallpaper/badge images and replace their URLs with local storage references.")
    parser.add_argument("table", choices=("all", "wallpapers", "badges"), nargs="?", default="all")
    parser.add_argument("--dry-run", action="store_true",
                        help="List remote images without downloading or changing anything")
    arguments = parser.parse_args(sys.argv[2:])
    failed = 0
    for label, model, uploads in (("wallpapers", Wallpaper, WallpaperUploads),
                                  ("badges", Badge, BadgeUploads)):
        if arguments.table in ("all", label):
            failed += localize(model.all(), uploads, label, arguments.dry_run)
    if failed:
        raise SystemExit(1)
