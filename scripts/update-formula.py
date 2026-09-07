#!/usr/bin/env python3
"""Update the formula only after verifying all four release archives."""

import argparse
import hashlib
import re
from pathlib import Path


def release_version(value):
    version = value.removeprefix("v")
    if len(version) > 80 or not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z]+(?:\.[0-9A-Za-z]+)*)?", version):
        raise ValueError("Expected a version such as 0.1.0-alpha.1")
    return version


def version_key(value):
    core, _, suffix = release_version(value).partition("-")
    identifiers = tuple((0, int(part)) if part.isdigit() else (1, part) for part in suffix.split("."))
    return tuple(map(int, core.split("."))), not suffix, identifiers


def verified_archives(assets, version):
    sums = {}
    for line in (assets / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (?:\./)?([^/\\]+)", line)
        if not match or match[2] in sums:
            raise ValueError("Invalid or duplicate checksum entry")
        sums[match[2]] = match[1]
    result = {}
    for platform in ("darwin", "linux"):
        for architecture in ("amd64", "arm64"):
            name = f"unswell_{version}_{platform}_{architecture}.tar.gz"
            digest = sums.get(name)
            if digest is None:
                raise ValueError(f"Missing checksum: {name}")
            with (assets / name).open("rb") as archive:
                actual = hashlib.file_digest(archive, "sha256").hexdigest()
            if actual != digest:
                raise ValueError(f"Checksum mismatch: {name}")
            result[platform, architecture] = (name, digest)
    return result


def release_block(version, archives):
    lines = []
    for platform, selector in (("darwin", "on_macos"), ("linux", "on_linux")):
        lines.append(f"  {selector} do")
        for architecture, cpu in (("arm64", "on_arm"), ("amd64", "on_intel")):
            name, digest = archives[platform, architecture]
            lines.extend([
                f"    {cpu} do",
                f'      url "https://github.com/stokaro/unswell/releases/download/v{version}/{name}"',
                f'      sha256 "{digest}"',
                "    end",
            ])
        lines.extend(["  end", ""])
    return "\n".join(lines).rstrip() + "\n"


def update(formula, assets, value):
    version = release_version(value)
    archives = verified_archives(assets, version)
    contents = formula.read_text(encoding="utf-8")
    previous = re.findall(r"/releases/download/v([^/]+)/", contents)
    if any(version_key(version) < version_key(old) for old in previous):
        raise ValueError("Automatic release updates cannot downgrade the formula")
    contents = replace_section(contents, "RELEASE", release_block(version, archives))
    formula.write_text(contents, encoding="utf-8")


def replace_section(contents, section, value):
    begin, end = f"  # BEGIN {section}\n", f"  # END {section}\n"
    if contents.count(begin) != 1 or contents.count(end) != 1:
        raise ValueError("Formula release markers are missing or repeated")
    before, rest = contents.split(begin)
    if end not in rest:
        raise ValueError("Formula release markers are out of order")
    _, after = rest.split(end)
    return before + begin + value + end + after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--formula", type=Path, default=Path("Formula/unswell.rb"))
    args = parser.parse_args()
    try:
        update(args.formula, args.assets, args.version)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Formula update failed: {error}\n")


if __name__ == "__main__":
    main()
