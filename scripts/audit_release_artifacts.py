#!/usr/bin/env python3
"""Fail if release artifacts contain files that should not ship to PyPI."""

from __future__ import annotations

import argparse
import re
import sys
import tarfile
import zipfile
from pathlib import Path


FORBIDDEN_PATH_PATTERNS = [
    re.compile(r"(^|/)(tests|node_modules)(/|$)"),
    re.compile(r"(^|/)\.(codegraph|codeboarding)(/|$)"),
    re.compile(r"(^|/)docs/plans/"),
    re.compile(r"(^|/)scripts/out/"),
    re.compile(r"(^|/)package-lock\.json$"),
    re.compile(r"(^|/)package\.json$"),
    re.compile(r"(^|/)scripts/whatsapp-bridge/"),
]

SECRET_PATTERNS = [
    re.compile(rb"sk-proj-[A-Za-z0-9_-]{20,}"),
    re.compile(rb"sk-[A-Za-z0-9]{32,}"),
]


def _iter_tar(path: Path):
    with tarfile.open(path, "r:*") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                yield member.name, None
                continue
            extracted = archive.extractfile(member)
            yield member.name, extracted.read() if extracted else b""


def _iter_zip(path: Path):
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                yield info.filename, None
                continue
            yield info.filename, archive.read(info)


def _iter_artifact(path: Path):
    if path.suffix == ".whl":
        yield from _iter_zip(path)
    elif path.name.endswith((".tar.gz", ".tgz")):
        yield from _iter_tar(path)
    else:
        raise ValueError(f"Unsupported artifact type: {path}")


def audit_artifact(path: Path) -> list[str]:
    findings: list[str] = []
    for name, content in _iter_artifact(path):
        normalized = name.strip("/")
        for pattern in FORBIDDEN_PATH_PATTERNS:
            if pattern.search(normalized):
                findings.append(f"{path.name}: forbidden path {normalized}")
                break
        if content:
            for pattern in SECRET_PATTERNS:
                if pattern.search(content):
                    findings.append(f"{path.name}: secret-like token in {normalized}")
                    break
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", nargs="+", type=Path)
    args = parser.parse_args(argv)

    findings: list[str] = []
    for artifact in args.artifacts:
        if not artifact.exists():
            findings.append(f"missing artifact: {artifact}")
            continue
        findings.extend(audit_artifact(artifact))

    if findings:
        print("Release artifact audit failed:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1

    print(f"Release artifact audit passed for {len(args.artifacts)} artifact(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
