#!/usr/bin/env python3
"""Compare Ubuntu 26.04 LTS disk hash from HyperV_UbuntuGallery.json against the remote Canonical SHA256SUMS."""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import urlopen


def _sanitize_json(content: str) -> str:
    # Remove trailing commas before closing braces/brackets so malformed JSON still parses.
    content = re.sub(r",\s*(?=[}\]])", "", content)
    return content


def get_json_hash(manifest_path: Path, image_name: str) -> str:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    with manifest_path.open("r", encoding="utf-8") as handle:
        raw = handle.read()

    sanitized = _sanitize_json(raw)
    data = json.loads(sanitized)

    images = data.get("images")
    if not isinstance(images, list):
        raise ValueError("Manifest JSON missing 'images' array.")

    for image in images:
        if image.get("name") == image_name:
            disk = image.get("disk")
            if not disk or "hash" not in disk:
                raise ValueError(f"Disk hash not found for image '{image_name}'.")
            return re.sub(r"^sha256:\s*|^SHA256:\s*", "", disk["hash"])  # type: ignore

    raise ValueError(f"Image '{image_name}' not found in manifest.")


def get_remote_hash(url: str, target_file: str) -> str:
    try:
        with urlopen(url) as response:
            content = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        raise ConnectionError(f"HTTP error retrieving remote SHA256SUMS: {exc.code} {exc.reason}") from exc
    except URLError as exc:
        raise ConnectionError(f"Error retrieving remote SHA256SUMS: {exc.reason}") from exc

    pattern = re.compile(rf"^\s*([A-Fa-f0-9]{{64}})\s+\*?{re.escape(target_file)}\s*$")
    for line in content.splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1)

    raise ValueError(f"Hash line for '{target_file}' not found in remote SHA256SUMS.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Ubuntu 26.04 LTS disk hash against Canonical SHA256SUMS.")
    parser.add_argument("--manifest", default="HyperV_UbuntuGallery.json", help="Path to the JSON manifest file.")
    parser.add_argument("--remote", default="https://partner-images.canonical.com/hyper-v/desktop/resolute/current/SHA256SUMS", help="Remote SHA256SUMS URL.")
    parser.add_argument("--name", default="Ubuntu 26.04 LTS", help="Image name to look up in the manifest.")
    parser.add_argument("--file", default="ubuntu-resolute-hyperv-amd64v3-ubuntu-desktop-hyperv.vhdx.zip", help="Filename to match in the remote SHA256SUMS.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)

    try:
        local_hash = get_json_hash(manifest_path, args.name)
        remote_hash = get_remote_hash(args.remote, args.file)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Local hash : {local_hash}")
    print(f"Remote hash: {remote_hash}")

    if local_hash.lower() == remote_hash.lower():
        print("✅ Newest already exists: the manifest hash matches the latest remote SHA256SUMS.")
        return 0

    print("⚠️ New version exists: manifest hash does not match the latest remote SHA256SUMS.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
