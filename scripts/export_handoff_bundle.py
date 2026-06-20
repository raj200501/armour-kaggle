#!/usr/bin/env python3
"""Build a deterministic, review-focused Kaggle/FDE handoff bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "armour_kaggle_handoff"

INCLUDED_FILES = (
    "README.md",
    "LICENSE",
    "docs/KAGGLE_FDE_HANDOFF_PACKET.md",
    "docs/KAGGLE_HARBOR_PORT_PLAN.md",
    "docs/KAGGLE_LAUNCH_SPEC.md",
    "docs/BENCHMARK_CARD.md",
    "docs/HARBOR_OUTPUT_CONTRACT.md",
    "docs/AUTOMATION_BENCH_REVIEW.md",
    "benchmark/dataset.toml",
    "benchmark/metric.py",
    "results/validation_summary.json",
)

INCLUDED_DIRECTORIES = (
    "benchmark/customer-ticket-data-scope",
)

EXCLUDED_PARTS = {"__pycache__", "outputs"}


def build_bundle(output: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    """Create the bundle and return its parsed manifest."""
    output = output.resolve()
    if output == ROOT or output in ROOT.parents:
        raise ValueError("Output must be a dedicated bundle directory")

    sources = list(_source_files())
    missing = [path for path in sources if not path.is_file()]
    if missing:
        names = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        raise FileNotFoundError(f"Missing handoff source files: {names}")

    if output.is_symlink():
        raise ValueError("Refusing to replace a symlinked output directory")
    if output.exists() and any(output.iterdir()):
        existing_manifest = output / "MANIFEST.json"
        if not existing_manifest.is_file():
            raise ValueError(
                "Refusing to replace a non-empty directory without an existing "
                "Armour handoff manifest"
            )
        existing = json.loads(existing_manifest.read_text(encoding="utf-8"))
        if existing.get("bundle") != "armour_kaggle_handoff":
            raise ValueError("Refusing to replace an unrelated output directory")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    entries = []
    for source in sources:
        relative = source.relative_to(ROOT)
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        entries.append(_manifest_entry(destination, relative))

    entries.sort(key=lambda item: item["path"])
    manifest: dict[str, object] = {
        "schema_version": "armour-handoff-manifest-v1",
        "bundle": "armour_kaggle_handoff",
        "source_repository": "https://github.com/raj200501/armour-kaggle",
        "manifest_scope": "All bundle files except MANIFEST.json itself.",
        "file_count": len(entries),
        "files": entries,
    }
    (output / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    validate_bundle(output, minimum_files=10)
    return manifest


def validate_bundle(output: Path, minimum_files: int = 10) -> None:
    """Validate manifest coverage and hashes for an existing bundle."""
    manifest_path = output / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("files", [])
    if manifest.get("file_count") != len(entries) or len(entries) < minimum_files:
        raise ValueError("Handoff manifest has an invalid file count")

    expected_paths = {entry["path"] for entry in entries}
    actual_paths = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file() and path.name != "MANIFEST.json"
    }
    if expected_paths != actual_paths:
        raise ValueError("Handoff manifest does not cover the exact bundle contents")

    for entry in entries:
        path = output / entry["path"]
        if path.stat().st_size != entry["bytes"]:
            raise ValueError(f"Size mismatch for {entry['path']}")
        if _sha256(path) != entry["sha256"]:
            raise ValueError(f"SHA256 mismatch for {entry['path']}")


def _source_files() -> tuple[Path, ...]:
    files = [ROOT / relative for relative in INCLUDED_FILES]
    for relative in INCLUDED_DIRECTORIES:
        directory = ROOT / relative
        if not directory.is_dir():
            files.append(directory)
            continue
        files.extend(
            path
            for path in sorted(directory.rglob("*"))
            if path.is_file()
            and not EXCLUDED_PARTS.intersection(path.relative_to(directory).parts)
            and path.suffix != ".pyc"
        )
    return tuple(files)


def _manifest_entry(path: Path, relative: Path) -> dict[str, object]:
    return {
        "path": relative.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = build_bundle(args.output)
    print(
        f"Wrote {manifest['file_count']} files and MANIFEST.json to "
        f"{args.output.resolve()}"
    )


if __name__ == "__main__":
    main()
