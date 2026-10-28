#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "maquetacion"))
import build_book  # noqa: E402


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


original_marker_pages = build_book.marker_pages


def marker_pages_with_chapter_headings(pdf_path, entries):
    found = original_marker_pages(pdf_path, entries)
    reader = build_book.PdfReader(str(pdf_path))
    page_texts = [normalize(page.extract_text() or "") for page in reader.pages]

    for entry in entries:
        if entry.kind != "chapter":
            continue
        if " · " not in entry.label:
            raise RuntimeError(f"No se pudo separar el rótulo del capítulo: {entry.label}")
        heading, title = entry.label.split(" · ", 1)
        needle = normalize(f"{heading} {title}")
        matches = [number for number, text in enumerate(page_texts, 1) if needle in text]
        if len(matches) != 1:
            raise RuntimeError(
                f"No se localizó de forma única el inicio de {entry.label!r}: {matches}"
            )
        found[entry.key] = matches[0]

    return found


build_book.marker_pages = marker_pages_with_chapter_headings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    shared_css = REPO_ROOT / "maquetacion" / "estilo-libro-6x9.css"
    book_css = Path(__file__).with_name("layout-fixes.css")
    with tempfile.TemporaryDirectory(prefix="aquiles-maquetacion-") as temp_dir:
        stylesheet = Path(temp_dir) / "estilo-libro-6x9.css"
        stylesheet.write_text(
            shared_css.read_text(encoding="utf-8")
            + "\n\n"
            + book_css.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        build_book.build(
            Path(args.root).resolve(),
            Path(args.output).resolve(),
            stylesheet,
        )


if __name__ == "__main__":
    main()
