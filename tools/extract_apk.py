#!/usr/bin/env python3
"""Safely unpack all regular ZIP entries from a *local* Android APK.

Produces a SHA-256 manifest. Does not decompile, execute, license or upload files.
Requires Python 3.9 or newer.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile

CHUNK = 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 20 * 1024**3


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 tools/extract_apk.py /absolute/path/to/app.apk", file=sys.stderr)
        return 2

    apk = Path(sys.argv[1]).expanduser().resolve()
    if not apk.is_file():
        print(f"APK not found: {apk}", file=sys.stderr)
        return 2

    base = Path.cwd() / "local-apk-inspection" / apk.stem
    extracted = base / "extracted"
    if base.exists():
        print(f"Refusing to overwrite existing inspection: {base}", file=sys.stderr)
        return 2

    files = []
    seen = set()

    try:
        with zipfile.ZipFile(apk) as archive:
            infos = archive.infolist()
            total = sum(info.file_size for info in infos if not info.is_dir())
            if total > MAX_UNCOMPRESSED_BYTES:
                raise ValueError("APK exceeds the safe 20-GiB uncompressed-size limit")

            # Validate the ENTIRE file list before writing to disk.
            for info in infos:
                name = info.filename
                parts = PurePosixPath(name).parts
                if (not name or name.startswith("/") or "\\" in name
                    or ":" in name or any(p in ("", ".", "..") for p in parts)
                    or any(ord(ch) < 32 for ch in name)):
                    raise ValueError(f"Unsafe ZIP member path: {name!r}")
                normalized = str(PurePosixPath(name))
                if not info.is_dir():
                    if normalized in seen:
                        raise ValueError(f"Duplicate ZIP member: {normalized}")
                    seen.add(normalized)
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_IFMT(mode) == stat.S_IFLNK:
                    raise ValueError(f"Symbolic-link ZIP member not permitted: {name}")

            extracted.mkdir(parents=True)
            for info in infos:
                rel = PurePosixPath(info.filename)
                output = extracted.joinpath(*rel.parts)
                if info.is_dir():
                    output.mkdir(parents=True, exist_ok=True)
                    continue

                output.parent.mkdir(parents=True, exist_ok=True)
                digest = hashlib.sha256()
                count = 0
                with archive.open(info) as src, output.open("xb") as dst:
                    while True:
                        block = src.read(CHUNK)
                        if not block:
                            break
                        dst.write(block)
                        digest.update(block)
                        count += len(block)
                files.append({"path": str(rel), "size": count, "sha256": digest.hexdigest()})

        with (base / "manifest.sha256").open("w", encoding="utf-8") as f:
            for item in sorted(files, key=lambda entry: entry["path"]):
                f.write(f'{item["sha256"]}  {item["path"]}\n')

        with (base / "summary.json").open("w", encoding="utf-8") as f:
            json.dump({"apk_name": apk.name, "file_count": len(files),
                       "total_extracted_bytes": sum(x["size"] for x in files),
                       "status": "local inspection only; not licensed for redistribution"},
                      f, indent=2)
            f.write("\n")

        print(f"Extracted {len(files)} files into {extracted}")
        print(f"SHA-256 inventory: {base / 'manifest.sha256'}")
        print(f"Summary: {base / 'summary.json'}")
        print("No files have been uploaded.")
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
        print(f"Extraction failed: {exc}", file=sys.stderr)
        print("A partial local directory may remain; inspect before retrying.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
