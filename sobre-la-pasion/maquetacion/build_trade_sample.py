#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from weasyprint import HTML

from build_full import ensure_seal, md, strip_part_marker

CSS = r'''
@page { size: 152.4mm 228.6mm; }

@page part {
  margin: 0;
}

@page opening:right {
  margin: 23mm 16.5mm 19mm 20mm;
  counter-increment: bodyPage;
  @bottom-right {
    content: counter(bodyPage);
    font: 8pt "EB Garamond";
    color: #666;
  }
}
@page opening:left {
  margin: 23mm 20mm 19mm 16.5mm;
  counter-increment: bodyPage;
  @bottom-left {
    content: counter(bodyPage);
    font: 8pt "EB Garamond";
    color: #666;
  }
}

@page body:right {
  margin: 17mm 16.5mm 19mm 20mm;
  counter-increment: bodyPage;
  @top-left {
    content: "AFRODITA AREIA · I";
    font: 7.6pt "EB Garamond";
    color: #1E4C45;
    letter-spacing: .04em;
    border-bottom: .45pt solid #D4D4D4;
    padding-bottom: 1.6mm;
  }
  @top-right {
    content: "SOBRE LA PASIÓN";
    font: 7.4pt "EB Garamond";
    color: #666;
    border-bottom: .45pt solid #D4D4D4;
    padding-bottom: 1.6mm;
  }
  @bottom-right {
    content: counter(bodyPage);
    font: 8pt "EB Garamond";
    color: #666;
  }
}
@page body:left {
  margin: 17mm 20mm 19mm 16.5mm;
  counter-increment: bodyPage;
  @top-left {
    content: "SOBRE LA PASIÓN";
    font: 7.4pt "EB Garamond";
    color: #666;
    border-bottom: .45pt solid #D4D4D4;
    padding-bottom: 1.6mm;
  }
  @top-right {
    content: "AFRODITA AREIA · I";
    font: 7.6pt "EB Garamond";
    color: #1E4C45;
    letter-spacing: .04em;
    border-bottom: .45pt solid #D4D4D4;
    padding-bottom: 1.6mm;
  }
  @bottom-left {
    content: counter(bodyPage);
    font: 8pt "EB Garamond";
    color: #666;
  }
}

html {
  counter-reset: bodyPage 0;
}
html, body {
  margin: 0;
  padding: 0;
  font-family: "EB Garamond", Garamond, serif;
  color: #262626;
}

.part-page {
  page: part;
  break-after: page;
  height: 228.6mm;
  box-sizing: border-box;
  text-align: center;
  padding: 44mm 18mm 20mm;
}
.part-page img {
  width: 24mm;
  height: 24mm;
  object-fit: contain;
}
.part-page .series {
  margin-top: 4mm;
  color: #1E4C45;
  font-size: 11pt;
  font-variant: small-caps;
  letter-spacing: .08em;
}
.part-page .rule {
  width: 58mm;
  border-top: .65pt solid #1E4C45;
  margin: 4mm auto 12mm;
}
.part-page h1 {
  margin: 0;
  font-size: 23pt;
  font-weight: 600;
  line-height: 1.1;
}
.part-page h2 {
  margin: 4mm 0 0;
  font-size: 15pt;
  font-weight: 400;
  line-height: 1.2;
}
.part-page .epigraph {
  margin-top: 7mm;
  color: #666;
  font-size: 10.5pt;
  line-height: 1.35;
  font-style: italic;
}

.chapter {
  page: body;
  font-size: 11.3pt;
  line-height: 1.39;
  hyphens: auto;
  orphans: 3;
  widows: 3;
}
.chapter > h1:first-of-type {
  page: opening;
  break-before: page;
  margin: 5mm 0 1.5mm;
  text-align: center;
  font-size: 11pt;
  font-weight: 400;
  color: #777;
  letter-spacing: .045em;
  text-transform: uppercase;
}
.chapter > h2:first-of-type {
  text-align: center;
  font-size: 22pt;
  line-height: 1.08;
  font-weight: 600;
  margin: 0 0 5mm;
}
.chapter > h2:first-of-type:after {
  content: "";
  display: block;
  width: 33mm;
  margin: 4.5mm auto 0;
  border-top: .75pt solid #1E4C45;
}
.chapter > blockquote:first-of-type {
  max-width: 93mm;
  margin: 5.5mm auto 8mm;
  padding: 0;
  border: 0;
  text-align: center;
  color: #555;
  font-size: 10.5pt;
  line-height: 1.38;
  font-style: italic;
}
.chapter p {
  margin: 0;
  text-align: justify;
  text-indent: 1.15em;
}
.chapter h3 + p,
.chapter blockquote + p,
.chapter hr + p,
.chapter > h2 + p,
.chapter > h1 + p {
  text-indent: 0;
}
.chapter h3 {
  break-after: avoid;
  margin: 5.4mm 0 2.2mm;
  color: #1E4C45;
  font-size: 12.2pt;
  line-height: 1.18;
  font-weight: 600;
}
.chapter blockquote:not(:first-of-type) {
  margin: 4.5mm 3mm;
  padding: 1.3mm 0 1.3mm 4mm;
  border-left: 1.4pt solid #1E4C45;
  color: #555;
  font-size: 10.7pt;
  line-height: 1.36;
  font-style: italic;
}
.chapter hr {
  border: 0;
  border-top: .45pt solid #D7D7D7;
  margin: 5mm 0;
}
.notes-title {
  margin-top: 7mm !important;
}
.notes {
  font-size: 9.5pt;
  line-height: 1.34;
  color: #444;
}
.notes p {
  margin: 0 0 2.2mm;
  text-indent: 0;
  text-align: justify;
}
'''

def part_html(root: Path) -> str:
    lines = [
        re.sub(r'[*#>_\x60]', '', line).strip()
        for line in (root / '08.md').read_text(encoding='utf-8').splitlines()
        if line.strip()
    ]
    part = lines[0] if lines else 'Parte I'
    subtitle = lines[1] if len(lines) > 1 else 'El caos y la posibilidad'
    epigraph = lines[2] if len(lines) > 2 else ''
    return (
        '<section class="part-page">'
        '<img src="assets/logo-green.png">'
        '<div class="series">AFRODITA AREIA · I</div>'
        '<div class="rule"></div>'
        f'<h1>{html.escape(part)}</h1>'
        f'<h2>{html.escape(subtitle)}</h2>'
        f'<div class="epigraph">{html.escape(epigraph)}</div>'
        '</section>'
    )

def chapter_html(root: Path) -> str:
    raw = strip_part_marker((root / '09.md').read_text(encoding='utf-8'))
    rendered = md.render(raw)
    if '<h3>Notas</h3>' in rendered:
        rendered = rendered.replace(
            '<h3>Notas</h3>',
            '<h3 class="notes-title">Notas</h3><div class="notes">',
            1,
        )
        rendered += '</div>'
    return '<section class="chapter">' + rendered + '</section>'

def build(root: Path, output: Path) -> None:
    ensure_seal(root)
    work = output.with_name(output.stem + '-source.pdf')
    doc = (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f'<style>{CSS}</style></head><body>'
        + part_html(root)
        + chapter_html(root)
        + '</body></html>'
    )
    HTML(string=doc, base_url=str(root)).write_pdf(str(work), presentational_hints=True)

    reader = PdfReader(str(work))
    notes_page = None
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ''
        if 'Notas' in text:
            notes_page = i
            break
    if notes_page is None:
        raise RuntimeError('No fue posible localizar la página de notas.')

    picks = [0, 1, 2, 3, notes_page]
    unique = []
    for idx in picks:
        if idx not in unique:
            unique.append(idx)
    if len(unique) < 5:
        for idx in range(4, len(reader.pages)):
            if idx not in unique and idx != notes_page:
                unique.insert(-1, idx)
            if len(unique) >= 5:
                break

    writer = PdfWriter()
    for idx in unique[:5]:
        writer.add_page(reader.pages[idx])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('wb') as fh:
        writer.write(fh)

    manifest = output.with_suffix('.txt')
    labels = [
        'Transición de Parte I',
        'Apertura de Capítulo 1',
        'Página corrida 1',
        'Página corrida 2',
        'Página con notas',
    ]
    manifest.write_text(
        '\n'.join(f'{label}: página fuente {idx + 1}' for label, idx in zip(labels, unique[:5])),
        encoding='utf-8',
    )
    work.unlink(missing_ok=True)
    print(output)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    p.add_argument('--output', default='sobre-la-pasion/build/muestra-6x9.pdf')
    a = p.parse_args()
    build(Path(a.root).resolve(), Path(a.output).resolve())

if __name__ == '__main__':
    main()
