#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import html
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path

from markdown_it import MarkdownIt
from PIL import Image
from pypdf import PdfReader
from weasyprint import HTML


PUBLISHER = "Centro Multidisciplinario Meriadock Formación y Asesoría A.C."
MOTTO = "La fuerza interior nos impulsa, un pequeño apoyo de los demás nos bendice"

md = MarkdownIt("commonmark", {"html": True}).enable("table")


@dataclass(frozen=True)
class TocEntry:
    key: str
    label: str
    kind: str


@dataclass(frozen=True)
class Piece:
    kind: str
    key: str
    label: str
    raw: str = ""
    part: str = ""
    subtitle: str = ""
    epigraph: str = ""


def roman(value: int) -> str:
    pairs = (
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    )
    n = max(1, int(value))
    result: list[str] = []
    for amount, symbol in pairs:
        while n >= amount:
            result.append(symbol)
            n -= amount
    return "".join(result)


def clean_text(value: str) -> str:
    return re.sub(r"[*#>`_]", "", value).strip()


def slug_key(prefix: str, value: str) -> str:
    value = value.lower()
    value = value.translate(str.maketrans("áéíóúüñ", "aeiouun"))
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return f"{prefix}-{value}" if value else prefix


def marker(key: str, enabled: bool) -> str:
    if not enabled or not key:
        return ""
    return f'<span class="pdf-marker">[[IDX:{html.escape(key)}]]</span>'


def load_config(root: Path) -> dict:
    path = root / "maquetacion.json"
    if not path.exists():
        raise FileNotFoundError(f"Falta la configuración editorial: {path}")
    config = json.loads(path.read_text(encoding="utf-8"))
    required = ("series_header", "short_title", "cover", "back_cover")
    missing = [name for name in required if not config.get(name)]
    if missing:
        raise ValueError(f"Faltan campos en maquetacion.json: {missing}")
    return config


def ensure_seal(root: Path) -> Path:
    svg_path = root / "assets" / "logo.svg"
    output = root / "assets" / "logo-green.png"
    svg = svg_path.read_text(encoding="utf-8")
    match = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", svg)
    if not match:
        raise RuntimeError("El logo institucional no contiene la máscara PNG esperada.")

    source = Image.open(io.BytesIO(base64.b64decode(match.group(1)))).convert("RGBA")
    padding = max(1, round(max(source.size) * 0.06))
    target = Image.new(
        "RGBA",
        (source.width + padding * 2, source.height + padding * 2),
        (0, 0, 0, 0),
    )
    src = source.load()
    dst = target.load()
    green = (30, 76, 69)

    for y in range(source.height):
        for x in range(source.width):
            red, green_channel, blue, alpha = src[x, y]
            luminance = 0.2126 * red + 0.7152 * green_channel + 0.0722 * blue
            mask_alpha = round((255 - luminance) * (alpha / 255))
            if mask_alpha:
                dst[x + padding, y + padding] = (*green, mask_alpha)

    output.parent.mkdir(parents=True, exist_ok=True)
    target.save(output)
    return output


def title_page(root: Path) -> str:
    lines = [clean_text(line) for line in (root / "01.md").read_text(encoding="utf-8").splitlines() if line.strip()]
    title = lines[0] if lines else "Libro"
    subtitle = lines[1] if len(lines) > 1 else ""
    volume = lines[2] if len(lines) > 2 else ""
    author = lines[3] if len(lines) > 3 else ""
    collection = next((line for line in lines if line.lower().startswith("colección:")), "")
    publisher = next((line for line in lines if "Centro Multidisciplinario" in line), PUBLISHER)
    year_match = re.search(r"(20\d{2})", publisher)
    year = year_match.group(1) if year_match else "2026"
    publisher = re.sub(r"\s*·\s*20\d{2}\s*$", "", publisher).strip()
    esc = html.escape
    return (
        '<section class="title-page"><img class="seal" src="assets/logo-green.png">'
        '<div class="institution">Centro Multidisciplinario Meriadock</div>'
        '<div class="rule"></div><div class="org">Formación y Asesoría A.C.</div>'
        f'<div class="motto">“{esc(MOTTO)}”</div>'
        f'<div class="main">{esc(title.upper())}</div>'
        f'<div class="subtitle">{esc(subtitle)}</div>'
        f'<div class="volume">{esc(volume)}</div>'
        f'<div class="author">{esc(author)}</div>'
        f'<div class="bottom"><div class="collection">{esc(collection)}</div>'
        f'<div>{esc(publisher)}</div><div>{esc(year)}</div></div></section>'
    )


def first_heading(raw: str, level: int, prefix: str) -> tuple[str, str] | None:
    match = re.search(rf"^{'#' * level}\s+({re.escape(prefix)}[^\n]*)$", raw, re.M | re.I)
    if not match:
        return None
    return match.group(1).strip(), match.group(0)


def heading_title(raw: str, after: str) -> str:
    start = raw.find(after)
    if start < 0:
        return ""
    match = re.search(r"^##\s+([^\n]+)$", raw[start + len(after):], re.M)
    return match.group(1).strip() if match else ""


def parse_part(raw: str) -> tuple[str, str, str, str] | None:
    explicit = re.search(r"^#\s+(Parte\s+[IVXLCDM]+)\s*$", raw, re.M | re.I)
    if explicit:
        chapter = re.search(r"^#\s+Capítulo\s+\d+\s*$", raw, re.M | re.I)
        stop = chapter.start() if chapter else len(raw)
        prefix = raw[:stop]
        subtitle_match = re.search(r"^##\s+([^\n]+)$", prefix, re.M)
        subtitle = subtitle_match.group(1).strip() if subtitle_match else ""
        descriptor = ""
        if subtitle_match:
            tail = prefix[subtitle_match.end():]
            descriptor = clean_text(" ".join(line for line in tail.splitlines() if line.strip()))
        body = raw[stop:].lstrip() if chapter else ""
        return explicit.group(1).title(), subtitle, descriptor, body

    legacy = re.match(r"^\s*\*Parte\s+([IVXLCDM]+)\s+[—-]\s+([^*]+)\*\s*\n+", raw, re.I)
    if legacy:
        return f"Parte {legacy.group(1).upper()}", legacy.group(2).strip(), "", raw[legacy.end():]
    return None


def parse_body_files(root: Path, stems: list[str], config: dict) -> list[Piece]:
    pieces: list[Piece] = []
    part_index = 0
    inserted_parts = config.get("parts_before", {})
    for stem in stems:
        inserted = inserted_parts.get(stem)
        if inserted:
            part = str(inserted["part"])
            subtitle = str(inserted["subtitle"])
            descriptor = str(inserted.get("epigraph", ""))
            part_index += 1
            pieces.append(
                Piece(
                    "part",
                    slug_key("parte", part.split()[-1]),
                    f"{part} · {subtitle}",
                    part=part,
                    subtitle=subtitle,
                    epigraph=descriptor,
                )
            )
        raw = (root / f"{stem}.md").read_text(encoding="utf-8")
        parsed_part = parse_part(raw)
        if parsed_part:
            part, subtitle, descriptor, raw = parsed_part
            part_index += 1
            key = slug_key("parte", part.split()[-1])
            pieces.append(Piece("part", key, f"{part} · {subtitle}", part=part, subtitle=subtitle, epigraph=descriptor))
            if not raw.strip():
                continue

        chapter = first_heading(raw, 1, "Capítulo")
        if chapter:
            heading, full = chapter
            number_match = re.search(r"\d+", heading)
            number = number_match.group(0) if number_match else heading
            title = heading_title(raw, full)
            pieces.append(Piece("chapter", f"cap-{number}", f"{heading} · {title}", raw=raw))
            continue

        appendix = first_heading(raw, 1, "Apéndice")
        if appendix:
            heading, full = appendix
            title = heading_title(raw, full)
            label = f"{heading} · {title}" if title else heading
            pieces.append(Piece("appendix", slug_key("ap", title or heading), label, raw=raw))
            continue

        glossary = first_heading(raw, 1, "Glosario")
        if glossary:
            heading, _ = glossary
            pieces.append(Piece("glossary", "glosario", heading, raw=raw))
            continue

        pieces.append(Piece("body", slug_key("seccion", stem), stem, raw=raw))
    return pieces


def discover_stems(root: Path, config: dict, key: str, fallback: list[str]) -> list[str]:
    configured = config.get(key)
    if configured:
        return [str(item).removesuffix(".md") for item in configured]
    return fallback


def build_plan(root: Path, config: dict) -> tuple[list[Piece], list[TocEntry]]:
    front_stems = discover_stems(root, config, "frontmatter", ["05", "06", "07"])
    body_stems = discover_stems(
        root,
        config,
        "body",
        [path.stem for path in sorted(root.glob("[0-9][0-9].md")) if int(path.stem) >= 8],
    )
    front_labels = config.get("frontmatter_toc", {})
    pieces: list[Piece] = []
    toc: list[TocEntry] = []
    for stem in front_stems:
        raw = (root / f"{stem}.md").read_text(encoding="utf-8")
        entry = front_labels.get(stem)
        key = entry.get("key", "") if isinstance(entry, dict) else ""
        label = entry.get("label", "") if isinstance(entry, dict) else ""
        pieces.append(Piece("front", key, label or stem, raw=raw))
        if key and label:
            toc.append(TocEntry(key, label, "front"))

    body = parse_body_files(root, body_stems, config)
    pieces.extend(body)
    toc.extend(TocEntry(piece.key, piece.label, "appendix" if piece.kind in {"appendix", "glossary"} else piece.kind) for piece in body if piece.kind != "body")
    return pieces, toc


def toc_page(entries: list[TocEntry], numbers: dict[str, str] | None = None) -> str:
    numbers = numbers or {}
    rows = []
    for entry in entries:
        page_no = numbers.get(entry.key, "000")
        rows.append(
            f'<tr class="toc-{entry.kind}"><td class="toc-label">{html.escape(entry.label)}</td>'
            f'<td class="toc-leader"></td><td class="toc-page">{html.escape(page_no)}</td></tr>'
        )
    return (
        '<section class="toc"><h1>ÍNDICE</h1><table class="toc-table">'
        '<colgroup><col class="col-label"><col class="col-leader"><col class="col-page"></colgroup>'
        f'<tbody>{"".join(rows)}</tbody></table></section>'
    )


def part_html(piece: Piece, series_header: str, markers: bool, counted: bool) -> str:
    cls = "part-page counted" if counted else "part-page"
    return (
        f'<section class="{cls}">{marker(piece.key, markers)}'
        f'<img src="assets/logo-green.png"><div class="series">{html.escape(series_header)}</div>'
        f'<div class="rule"></div><h1>{html.escape(piece.part)}</h1>'
        f'<h2>{html.escape(piece.subtitle)}</h2><div class="epigraph">{html.escape(piece.epigraph)}</div></section>'
    )


def render_piece(piece: Piece, markers: bool) -> str:
    css_class = {
        "front": "frontmatter",
        "chapter": "chapter",
        "appendix": "appendix",
        "glossary": "glossary",
        "body": "warning-page",
    }[piece.kind]
    return f'<section class="{css_class}">{marker(piece.key, markers)}{md.render(piece.raw)}</section>'


def document_html(
    root: Path,
    config: dict,
    css: str,
    pieces: list[Piece],
    toc_entries: list[TocEntry],
    toc_numbers: dict[str, str] | None,
    markers: bool,
) -> str:
    cover = html.escape((root / config["cover"]).as_uri())
    back = html.escape((root / config["back_cover"]).as_uri())
    series_header = str(config["series_header"])
    short_title = str(config["short_title"])
    header = (
        '<div class="running-header-left"><img src="assets/logo-green.png">'
        f'<span class="book">{html.escape(series_header)}</span></div>'
        f'<div class="running-header-right">{html.escape(short_title)}</div>'
    )
    sections = [
        f'<section class="cover-page"><img src="{cover}"></section>',
        title_page(root),
        f'<section class="legal-page">{md.render((root / "02.md").read_text(encoding="utf-8"))}</section>',
        f'<section class="epigraph-page">{md.render((root / "03.md").read_text(encoding="utf-8"))}</section>',
        toc_page(toc_entries, toc_numbers),
    ]
    part_seen = 0
    for piece in pieces:
        if piece.kind == "part":
            part_seen += 1
            sections.append(part_html(piece, series_header, markers, counted=part_seen > 1))
        else:
            sections.append(render_piece(piece, markers))
    sections.append(f'<section class="cover-page"><img src="{back}"></section>')
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f'<style>{css}</style></head><body>{header}{"".join(sections)}</body></html>'
    )


def render_pdf(root: Path, config: dict, css: str, pieces: list[Piece], toc_entries: list[TocEntry], output: Path, numbers: dict[str, str] | None, markers: bool) -> None:
    HTML(
        string=document_html(root, config, css, pieces, toc_entries, numbers, markers),
        base_url=str(root),
    ).write_pdf(str(output), presentational_hints=True)


def marker_pages(pdf_path: Path, entries: list[TocEntry]) -> dict[str, int]:
    reader = PdfReader(str(pdf_path))
    found: dict[str, int] = {}
    for page_no, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        for entry in entries:
            if entry.key not in found and f"[[IDX:{entry.key}]]" in text:
                found[entry.key] = page_no
    missing = [entry.key for entry in entries if entry.key not in found]
    if missing:
        raise RuntimeError(f"No fue posible localizar marcadores del índice: {missing}")
    return found


def compute_toc_numbers(pages: dict[str, int], entries: list[TocEntry]) -> dict[str, str]:
    first_chapter = next((entry.key for entry in entries if entry.kind == "chapter"), None)
    if first_chapter is None:
        raise RuntimeError("El libro no contiene capítulos identificables.")
    body_start = pages[first_chapter]
    first_part = next((entry.key for entry in entries if entry.kind == "part"), None)
    result: dict[str, str] = {}
    for entry in entries:
        physical = pages[entry.key]
        if entry.kind == "front":
            result[entry.key] = roman(physical)
        elif entry.key == first_part:
            result[entry.key] = "1"
        else:
            result[entry.key] = str(physical - body_start + 1)
    return result


def build(root: Path, output: Path, stylesheet: Path) -> None:
    config = load_config(root)
    for asset in (config["cover"], config["back_cover"]):
        if not (root / asset).exists():
            raise FileNotFoundError(f"Falta el activo editorial: {root / asset}")
    ensure_seal(root)
    css = stylesheet.read_text(encoding="utf-8")
    pieces, toc_entries = build_plan(root, config)
    output.parent.mkdir(parents=True, exist_ok=True)
    pass1 = output.with_name(output.stem + ".pass1.pdf")
    pass2 = output.with_name(output.stem + ".pass2.pdf")
    render_pdf(root, config, css, pieces, toc_entries, pass1, None, True)
    numbers1 = compute_toc_numbers(marker_pages(pass1, toc_entries), toc_entries)
    render_pdf(root, config, css, pieces, toc_entries, pass2, numbers1, True)
    numbers2 = compute_toc_numbers(marker_pages(pass2, toc_entries), toc_entries)
    render_pdf(root, config, css, pieces, toc_entries, output, numbers2, False)
    pass1.unlink(missing_ok=True)
    pass2.unlink(missing_ok=True)
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--stylesheet",
        default=str(Path(__file__).with_name("estilo-libro-6x9.css")),
    )
    args = parser.parse_args()
    build(Path(args.root).resolve(), Path(args.output).resolve(), Path(args.stylesheet).resolve())


if __name__ == "__main__":
    main()
