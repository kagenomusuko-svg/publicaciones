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

@page part { margin: 0; }

@page body {
  margin: 19mm 16.5mm 19mm 20mm;
  counter-increment: bodyPage;
  @top-left {
    content: element(bookleft);
    border-bottom: .6pt solid #CFCFCF;
    padding-bottom: 2mm;
    vertical-align: bottom;
  }
  @top-center {
    content: " ";
    border-bottom: .6pt solid #CFCFCF;
  }
  @top-right {
    content: element(bookright);
    border-bottom: .6pt solid #CFCFCF;
    padding-bottom: 2mm;
    vertical-align: bottom;
  }
  @bottom-left {
    content: "Centro Multidisciplinario Meriadock Formación y Asesoría A.C.";
    font: 7.2pt "EB Garamond";
    color: #666;
    border-top: .5pt solid #D8D8D8;
    padding-top: 2mm;
  }
  @bottom-center {
    content: " ";
    border-top: .5pt solid #D8D8D8;
  }
  @bottom-right {
    content: counter(bodyPage);
    font: 7.2pt "EB Garamond";
    color: #666;
    border-top: .5pt solid #D8D8D8;
    padding-top: 2mm;
  }
}

html { counter-reset: bodyPage 0; }
html, body {
  margin: 0;
  padding: 0;
  font-family: "EB Garamond", Garamond, serif;
  color: #262626;
}

.running-header-left {
  position: running(bookleft);
  display: flex;
  align-items: center;
  white-space: nowrap;
}
.running-header-left img {
  width: 8mm;
  height: 8mm;
  object-fit: contain;
  margin-right: 3mm;
}
.running-header-left .book {
  font: 700 8pt "EB Garamond";
  color: #1E4C45;
  letter-spacing: .04em;
}
.running-header-right {
  position: running(bookright);
  white-space: nowrap;
  text-align: right;
  font: 7.5pt "EB Garamond";
  color: #666;
}

.part-page {
  page: part;
  break-after: page;
  height: 228.6mm;
  box-sizing: border-box;
  text-align: center;
  padding-top: 46mm;
}
.part-page img {
  width: 28mm;
  height: 28mm;
  object-fit: contain;
}
.part-page .series {
  margin-top: 5mm;
  color: #1E4C45;
  font-size: 14pt;
  font-variant: small-caps;
  letter-spacing: .08em;
}
.part-page .rule {
  width: 75mm;
  border-top: .7pt solid #1E4C45;
  margin: 5mm auto 14mm;
}
.part-page h1 {
  font-size: 27pt;
  margin: 0;
}
.part-page h2 {
  font-size: 17pt;
  color: #262626;
  font-weight: 400;
  margin-top: 5mm;
}
.part-page .epigraph {
  margin-top: 8mm;
  color: #666;
  font-size: 11pt;
  font-style: italic;
}

.chapter {
  page: body;
  break-before: page;
  font-size: 11.3pt;
  line-height: 1.36;
}
p {
  margin: 0 0 3.2mm;
  text-align: justify;
}
h1, h2, h3 {
  line-height: 1.25;
  color: #222;
}
h1 {
  font-size: 17pt;
  margin: 8mm 0 3mm;
}
h2 {
  font-size: 14pt;
  margin: 7mm 0 2.8mm;
}
h3 {
  font-size: 12pt;
  color: #1E4C45;
  margin: 6mm 0 2.3mm;
}
blockquote {
  margin: 5mm 0;
  padding: 1mm 0 1mm 5mm;
  border-left: 1.6pt solid #1E4C45;
  color: #555;
  font-style: italic;
}
hr {
  border: 0;
  border-top: .5pt solid #D8D8D8;
  margin: 6mm 0;
}
ul, ol {
  margin: 0 0 4mm 6mm;
  padding-left: 5mm;
}
li { margin-bottom: 1.5mm; }

.chapter > p:first-child {
  text-align: center;
  color: #1E4C45;
  font-variant: small-caps;
  letter-spacing: .04em;
}
.chapter > h1:first-of-type {
  text-align: center;
  font-size: 13pt;
  font-weight: 400;
  color: #666;
  margin-top: 6mm;
}
.chapter > h2:first-of-type {
  text-align: center;
  font-size: 24pt;
  line-height: 1.1;
  margin: 2mm 0 6mm;
}
.chapter > h2:first-of-type:after {
  content: "";
  display: block;
  width: 42mm;
  margin: 5mm auto 0;
  border-top: .8pt solid #1E4C45;
}
.chapter > blockquote:first-of-type {
  max-width: 93mm;
  margin: 6mm auto 9mm;
}

.notes-title {
  margin-top: 7mm !important;
}
.notes {
  font-size: 9.8pt;
  line-height: 1.35;
  color: #444;
}
.notes p {
  margin: 0 0 2.3mm;
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
        + '<div class="running-header-left"><img src="assets/logo-green.png"><span class="book">AFRODITA AREIA · I</span></div>'
        + '<div class="running-header-right">SOBRE LA PASIÓN</div>'
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
    p.add_argument('--output', default='afrodita-areia/sobre-la-pasion/build/muestra-6x9.pdf')
    a = p.parse_args()
    build(Path(a.root).resolve(), Path(a.output).resolve())

if __name__ == '__main__':
    main()
