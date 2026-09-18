#!/usr/bin/env python3
from __future__ import annotations

import argparse, base64, html, io, re
from pathlib import Path
from markdown_it import MarkdownIt
from PIL import Image
from weasyprint import HTML
from pypdf import PdfReader

GREEN = '#1E4C45'
TEXT = '#262626'
MUTED = '#666666'
RULE = '#D8D8D8'
PUBLISHER = 'Centro Multidisciplinario Meriadock Formación y Asesoría A.C.'
MOTTO = 'La fuerza interior nos impulsa, un pequeño apoyo de los demás nos bendice'

CSS = r'''
@page { size: 152.4mm 228.6mm; }
@page cover { margin: 0; }
@page title { margin: 0; }
@page legal { margin: 22mm 16.5mm 22mm 20mm; }
@page epigraph { margin: 0; }
@page part { margin: 0; }
@page part-body { margin: 0; counter-increment: bodyPage; }
@page front {
  margin: 19mm 16.5mm 19mm 20mm;
  @top-left { content: element(bookleft); border-bottom: .6pt solid #CFCFCF; padding-bottom: 2mm; vertical-align: bottom; }
  @top-center { content: " "; border-bottom: .6pt solid #CFCFCF; }
  @top-right { content: element(bookright); border-bottom: .6pt solid #CFCFCF; padding-bottom: 2mm; vertical-align: bottom; }
  @bottom-left { content: "Centro Multidisciplinario Meriadock Formación y Asesoría A.C."; font: 7.2pt "EB Garamond"; color: #666; border-top: .5pt solid #D8D8D8; padding-top: 2mm; }
  @bottom-center { content: " "; border-top: .5pt solid #D8D8D8; }
  @bottom-right { content: counter(page, upper-roman); font: 7.2pt "EB Garamond"; color: #666; border-top: .5pt solid #D8D8D8; padding-top: 2mm; }
}
@page body {
  margin: 19mm 16.5mm 19mm 20mm;
  counter-increment: bodyPage;
  @top-left { content: element(bookleft); border-bottom: .6pt solid #CFCFCF; padding-bottom: 2mm; vertical-align: bottom; }
  @top-center { content: " "; border-bottom: .6pt solid #CFCFCF; }
  @top-right { content: element(bookright); border-bottom: .6pt solid #CFCFCF; padding-bottom: 2mm; vertical-align: bottom; }
  @bottom-left { content: "Centro Multidisciplinario Meriadock Formación y Asesoría A.C."; font: 7.2pt "EB Garamond"; color: #666; border-top: .5pt solid #D8D8D8; padding-top: 2mm; }
  @bottom-center { content: " "; border-top: .5pt solid #D8D8D8; }
  @bottom-right { content: counter(bodyPage); font: 7.2pt "EB Garamond"; color: #666; border-top: .5pt solid #D8D8D8; padding-top: 2mm; }
}
html { counter-reset: bodyPage 0; }
html, body { margin: 0; padding: 0; font-family: "EB Garamond", Garamond, serif; color: #262626; }
.running-header-left { position: running(bookleft); display: flex; align-items: center; white-space: nowrap; }
.running-header-left img { width: 8mm; height: 8mm; object-fit: contain; margin-right: 3mm; }
.running-header-left .book { font: 700 8pt "EB Garamond"; color: #1E4C45; letter-spacing: .04em; }
.running-header-right { position: running(bookright); white-space: nowrap; text-align: right; font: 7.5pt "EB Garamond"; color: #666; }
.cover-page { page: cover; break-after: page; width: 152.4mm; height: 228.6mm; }
.cover-page img { width: 152.4mm; height: 228.6mm; object-fit: fill; display: block; }
.title-page { page: title; break-after: page; height: 228.6mm; box-sizing: border-box; text-align: center; padding: 18mm 15mm 17mm; position: relative; }
.title-page .seal { width: 28mm; height: 28mm; object-fit: contain; }
.title-page .institution { margin-top: 5mm; color: #1E4C45; font: 600 13pt "EB Garamond"; letter-spacing: .07em; text-transform: uppercase; }
.title-page .rule { width: 70mm; margin: 3mm auto 2mm; border-top: .7pt solid #1E4C45; }
.title-page .org { color: #666; font-size: 9.5pt; }
.title-page .motto { color: #1E4C45; font-size: 8.5pt; font-style: italic; margin-top: 2.5mm; }
.title-page .main { margin-top: 24mm; font-size: 29pt; font-weight: 700; letter-spacing: .02em; }
.title-page .subtitle { margin-top: 6mm; color: #1E4C45; font-size: 21pt; font-style: italic; }
.title-page .volume { color: #666; font-size: 11pt; margin-top: 3mm; }
.title-page .author { margin-top: 19mm; font-size: 16pt; }
.title-page .bottom { position: absolute; left: 15mm; right: 15mm; bottom: 15mm; color: #666; font-size: 9.5pt; line-height: 1.5; }
.title-page .collection { font-style: italic; }
.legal-page { page: legal; break-after: page; font-size: 9pt; line-height: 1.45; color: #555; }
.legal-page h1, .legal-page h2 { color: #262626; font-size: 15pt; margin: 0 0 8mm; }
.epigraph-page { page: epigraph; break-after: page; height: 228.6mm; display: flex; align-items: center; justify-content: center; text-align: center; padding: 0 28mm; box-sizing: border-box; }
.epigraph-page blockquote { border: 0; margin: 0; color: #444; font-size: 14pt; line-height: 1.5; font-style: italic; }
.frontmatter { page: front; break-before: page; }
.part-page { page: part; break-before: page; break-after: page; height: 228.6mm; box-sizing: border-box; text-align: center; padding-top: 46mm; }
.part-page.counted { page: part-body; }
.part-page img { width: 28mm; height: 28mm; object-fit: contain; }
.part-page .series { margin-top: 5mm; color: #1E4C45; font-size: 14pt; font-variant: small-caps; letter-spacing: .08em; }
.part-page .rule { width: 75mm; border-top: .7pt solid #1E4C45; margin: 5mm auto 14mm; }
.part-page h1 { font-size: 27pt; margin: 0; }
.part-page h2 { font-size: 17pt; color: #262626; font-weight: 400; margin-top: 5mm; }
.part-page .epigraph { margin-top: 8mm; color: #666; font-size: 11pt; font-style: italic; }
.chapter, .appendix, .glossary, .warning-page { page: body; break-before: page; }
.frontmatter, .chapter, .appendix, .glossary, .warning-page { font-size: 11.3pt; line-height: 1.33; }
.appendix > h1:first-of-type, .glossary > h1:first-of-type, .warning-page > h1:first-of-type { text-align: center; font-size: 22pt; margin: 8mm 0 5mm; }
.appendix > h2:first-of-type { text-align: center; font-size: 18pt; margin: 2mm 0 3mm; }
.appendix > h3:first-of-type { text-align: center; font-size: 12pt; font-weight: 400; color: #666; margin: 0 0 7mm; }
.warning-page { padding-top: 18mm; }
.warning-page:before { content: ""; display:block; width: 48mm; margin: 0 auto 8mm; border-top: .8pt solid #1E4C45; }
.glossary h2 { break-after: avoid; color: #1E4C45; }
p { margin: 0 0 3.2mm; text-align: justify; }
h1, h2, h3 { line-height: 1.25; color: #222; }
h1 { font-size: 17pt; margin: 8mm 0 3mm; }
h2 { font-size: 14pt; margin: 7mm 0 2.8mm; }
h3 { font-size: 11.5pt; color: #1E4C45; margin: 6mm 0 2.3mm; }
blockquote { margin: 5mm 0; padding: 1mm 0 1mm 5mm; border-left: 1.6pt solid #1E4C45; color: #555; font-style: italic; }
hr { border: 0; border-top: .5pt solid #D8D8D8; margin: 6mm 0; }
ul, ol { margin: 0 0 4mm 6mm; padding-left: 5mm; }
li { margin-bottom: 1.5mm; }
.frontmatter > h1:first-child { font-size: 25pt; margin-top: 5mm; }
.chapter > p:first-child { text-align: center; color: #1E4C45; font-variant: small-caps; letter-spacing: .04em; }
.chapter > h1:first-of-type { text-align: center; font-size: 13pt; font-weight: 400; color: #666; margin-top: 6mm; }
.chapter > h2:first-of-type { text-align: center; font-size: 24pt; line-height: 1.1; margin: 2mm 0 6mm; }
.chapter > h2:first-of-type:after { content: ""; display: block; width: 42mm; margin: 5mm auto 0; border-top: .8pt solid #1E4C45; }
.chapter > blockquote:first-of-type { max-width: 93mm; margin: 6mm auto 9mm; }
.pdf-marker { position: absolute; left: 1mm; top: 1mm; color: #fff; font-size: 1pt; line-height: 1; }
.toc { page: front; break-before: page; }
.toc h1 { font-size: 25pt; margin: 5mm 0 8mm; }
table { width: 100%; border-collapse: collapse; font-size: 9pt; margin: 5mm 0; }
th, td { border: .5pt solid #D8D8D8; padding: 2mm; vertical-align: top; }
th { background: #F5F5F2; }
.toc-table { width: 100%; border-collapse: collapse; table-layout: fixed; margin: 0; font-size: 10pt; }
.toc-table .col-label { width: 72%; }
.toc-table .col-leader { width: 18%; }
.toc-table .col-page { width: 10%; }
.toc-table td { border: 0; padding: 0 0 2.1mm; vertical-align: bottom; background: transparent; }
.toc-table .toc-label { padding-right: 2mm; }
.toc-table .toc-leader { border-bottom: .5pt dotted #BEBEBE; }
.toc-table .toc-page { text-align: right; white-space: nowrap; color: #1E4C45; font-weight: 600; }
.toc-table tr.toc-part .toc-label,
.toc-table tr.toc-part .toc-page { color: #1E4C45; font-weight: 600; text-transform: uppercase; letter-spacing: .03em; padding-top: 2.8mm; }
.toc-table tr.toc-chapter .toc-label { padding-left: 5mm; }
.toc-table tr.toc-appendix .toc-label { padding-top: 1.4mm; }
'''

md = MarkdownIt('commonmark', {'html': True}).enable('table')

TOC_ENTRIES = [
    ('prefacio', 'Prefacio · El día que el caos llegó al Olimpo', 'front'),
    ('prologo', 'Prólogo · Por qué la voluntad necesita un nuevo comienzo', 'front'),
    ('parte-i', 'Parte I · El caos y la posibilidad', 'part'),
    ('cap-1', 'Capítulo 1 · El caos no es desorden', 'chapter'),
    ('cap-2', 'Capítulo 2 · Determinación y colapso', 'chapter'),
    ('cap-3', 'Capítulo 3 · Habitar el caos', 'chapter'),
    ('parte-ii', 'Parte II · La pasión como fuerza ontológica', 'part'),
    ('cap-4', 'Capítulo 4 · Qué es la pasión', 'chapter'),
    ('cap-5', 'Capítulo 5 · La pasión en los objetos', 'chapter'),
    ('cap-6', 'Capítulo 6 · La pasión en los organismos', 'chapter'),
    ('cap-7', 'Capítulo 7 · Las dos direcciones de la pasión', 'chapter'),
    ('parte-iii', 'Parte III · Las mediaciones', 'part'),
    ('cap-8', 'Capítulo 8 · La mediación prima', 'chapter'),
    ('cap-9', 'Capítulo 9 · La identidad como dimensión del ser', 'chapter'),
    ('cap-10', 'Capítulo 10 · La mediación fanes', 'chapter'),
    ('cap-11', 'Capítulo 11 · La mediación bis', 'chapter'),
    ('parte-iv', 'Parte IV · El ego como integral', 'part'),
    ('cap-12', 'Capítulo 12 · Las tres fórmulas: mapa del sistema', 'chapter'),
    ('cap-13', 'Capítulo 13 · El ego como proceso', 'chapter'),
    ('cap-14', 'Capítulo 14 · Las posibilidades negadas', 'chapter'),
    ('parte-v', 'Parte V · La pasión y el sujeto', 'part'),
    ('cap-15', 'Capítulo 15 · Antes del pensamiento, la pasión', 'chapter'),
    ('ap-a', 'Apéndice A · El aego. Afasia volitiva y singularidad ontológica', 'appendix'),
    ('ap-b', 'Apéndice B · Zagreo o la soberanía no consentida', 'appendix'),
    ('ap-c', 'Apéndice C · Narciso o la víctima indistinguible', 'appendix'),
    ('glosario', 'Glosario de términos', 'appendix'),
]

def roman(value: int) -> str:
    pairs = (
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I'),
    )
    n = max(1, int(value))
    result = []
    for amount, symbol in pairs:
        while n >= amount:
            result.append(symbol)
            n -= amount
    return ''.join(result)

def marker(key: str, enabled: bool) -> str:
    if not enabled:
        return ''
    return f'<span class="pdf-marker">[[IDX:{html.escape(key)}]]</span>'

def toc_page(numbers: dict[str, str] | None = None) -> str:
    numbers = numbers or {}
    rows = []
    for key, label, kind in TOC_ENTRIES:
        page_no = numbers.get(key, '000')
        rows.append(
            f'<tr class="toc-{kind}">'
            f'<td class="toc-label">{html.escape(label)}</td>'
            f'<td class="toc-leader"></td>'
            f'<td class="toc-page">{html.escape(page_no)}</td>'
            f'</tr>'
        )
    return (
        '<section class="toc"><h1>ÍNDICE</h1>'
        '<table class="toc-table">'
        '<colgroup><col class="col-label"><col class="col-leader"><col class="col-page"></colgroup>'
        '<tbody>'
        + ''.join(rows)
        + '</tbody></table></section>'
    )

def ensure_seal(root: Path) -> Path:
    """Replica la máscara/tinte de dialogos-eleatas/src/lib/seal.ts."""
    svg_path = root / 'assets' / 'logo.svg'
    output = root / 'assets' / 'logo-green.png'
    svg = svg_path.read_text(encoding='utf-8')
    match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', svg)
    if not match:
        raise RuntimeError('El logo institucional no contiene la máscara PNG esperada.')

    source = Image.open(io.BytesIO(base64.b64decode(match.group(1)))).convert('RGBA')
    padding = max(1, round(max(source.size) * 0.06))
    target = Image.new('RGBA', (source.width + padding * 2, source.height + padding * 2), (0, 0, 0, 0))
    src = source.load()
    dst = target.load()
    green = (30, 76, 69)

    for y in range(source.height):
        for x in range(source.width):
            r, g, b, a = src[x, y]
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            mask_alpha = round((255 - luminance) * (a / 255))
            if mask_alpha:
                dst[x + padding, y + padding] = (*green, mask_alpha)

    output.parent.mkdir(parents=True, exist_ok=True)
    target.save(output)
    return output

def clean_lines(raw: str):
    return [re.sub(r'[*#>`_]', '', x).strip() for x in raw.splitlines() if x.strip()]

def title_page(root: Path) -> str:
    lines = clean_lines((root/'01.md').read_text(encoding='utf-8'))
    title = lines[0] if lines else 'Afrodita Areia'
    subtitle = lines[1] if len(lines)>1 else 'Sobre la pasión'
    volume = lines[2] if len(lines)>2 else 'Volumen I'
    author = lines[3] if len(lines)>3 else 'Miguel Hilario Olvera Aguilar'
    collection = next((x for x in lines if x.lower().startswith('colección:')), 'Colección: Reivindicación ontológica del ego')
    publisher = next((x for x in lines if 'Centro Multidisciplinario' in x), PUBLISHER)
    year_match = re.search(r'(20\d{2})', publisher)
    year = year_match.group(1) if year_match else '2026'
    publisher = publisher.replace(' · 2026', '').strip()
    esc = html.escape
    return f'''<section class="title-page"><img class="seal" src="assets/logo-green.png"><div class="institution">Centro Multidisciplinario Meriadock</div><div class="rule"></div><div class="org">Formación y Asesoría A.C.</div><div class="motto">“{esc(MOTTO)}”</div><div class="main">{esc(title.upper())}</div><div class="subtitle">{esc(subtitle)}</div><div class="volume">{esc(volume)}</div><div class="author">{esc(author)}</div><div class="bottom"><div class="collection">{esc(collection)}</div><div>{esc(publisher.replace(' ·','').strip())}</div><div>{esc(year)}</div></div></section>'''

def epigraph(root: Path) -> str:
    return '<section class="epigraph-page">' + md.render((root/'03.md').read_text(encoding='utf-8')) + '</section>'

def part_page_from_text(
    part: str,
    subtitle: str,
    epigraph: str = '',
    *,
    marker_key: str = '',
    markers: bool = False,
    counted: bool = False,
) -> str:
    cls = 'part-page counted' if counted else 'part-page'
    return (
        f'<section class="{cls}">{marker(marker_key, markers)}'
        f'<img src="assets/logo-green.png"><div class="series">AFRODITA AREIA · I</div>'
        f'<div class="rule"></div><h1>{html.escape(part)}</h1>'
        f'<h2>{html.escape(subtitle)}</h2><div class="epigraph">{html.escape(epigraph)}</div></section>'
    )

def part_page(root: Path, markers: bool = False) -> str:
    lines = clean_lines((root/'08.md').read_text(encoding='utf-8'))
    return part_page_from_text(
        lines[0] if lines else 'Parte I',
        lines[1] if len(lines) > 1 else '',
        lines[2] if len(lines) > 2 else '',
        marker_key='parte-i',
        markers=markers,
        counted=False,
    )

def strip_part_marker(raw: str) -> str:
    return re.sub(r'^\s*\*Parte\s+[IVXLCDM]+\s+[—-]\s+[^*]+\*\s*\n+', '', raw, count=1, flags=re.I)

def chapter_piece(root: Path, stem: str, marker_key: str, markers: bool = False) -> str:
    raw = strip_part_marker((root/f'{stem}.md').read_text(encoding='utf-8'))
    return f'<section class="chapter">{marker(marker_key, markers)}' + md.render(raw) + '</section>'

def appendix_piece(root: Path, stem: str, marker_key: str, markers: bool = False) -> str:
    return (
        f'<section class="appendix">{marker(marker_key, markers)}'
        + md.render((root/f'{stem}.md').read_text(encoding='utf-8'))
        + '</section>'
    )

def render_piece(
    root: Path,
    stem: str,
    cls: str,
    marker_key: str = '',
    markers: bool = False,
) -> str:
    return (
        f'<section class="{cls}">{marker(marker_key, markers)}'
        + md.render((root/f'{stem}.md').read_text(encoding='utf-8'))
        + '</section>'
    )

def document_html(
    root: Path,
    toc_numbers: dict[str, str] | None = None,
    *,
    markers: bool = False,
) -> str:
    cover = html.escape((root/'Portada Vol I red.png').as_uri())
    back = html.escape((root/'Contra portada Vol I.png').as_uri())
    header = (
        '<div class="running-header-left"><img src="assets/logo-green.png">'
        '<span class="book">AFRODITA AREIA · I</span></div>'
        '<div class="running-header-right">SOBRE LA PASIÓN</div>'
    )

    sections = [
        f'<section class="cover-page"><img src="{cover}"></section>',
        title_page(root),
        render_piece(root, '02', 'legal-page'),
        epigraph(root),
        toc_page(toc_numbers),
        render_piece(root, '05', 'frontmatter'),
        render_piece(root, '06', 'frontmatter', 'prefacio', markers),
        render_piece(root, '07', 'frontmatter', 'prologo', markers),
        part_page(root, markers),
        chapter_piece(root, '09', 'cap-1', markers),
        chapter_piece(root, '10', 'cap-2', markers),
        chapter_piece(root, '11', 'cap-3', markers),
        part_page_from_text(
            'Parte II', 'La pasión como fuerza ontológica',
            marker_key='parte-ii', markers=markers, counted=True,
        ),
    ]

    for stem, key in (
        ('12', 'cap-4'), ('13', 'cap-5'), ('14', 'cap-6'), ('15', 'cap-7'),
    ):
        sections.append(chapter_piece(root, stem, key, markers))

    sections.append(part_page_from_text(
        'Parte III', 'Las mediaciones',
        marker_key='parte-iii', markers=markers, counted=True,
    ))
    for stem, key in (
        ('16', 'cap-8'), ('17', 'cap-9'), ('18', 'cap-10'), ('19', 'cap-11'),
    ):
        sections.append(chapter_piece(root, stem, key, markers))

    sections.append(part_page_from_text(
        'Parte IV', 'El ego como integral',
        marker_key='parte-iv', markers=markers, counted=True,
    ))
    for stem, key in (('20', 'cap-12'), ('21', 'cap-13'), ('22', 'cap-14')):
        sections.append(chapter_piece(root, stem, key, markers))

    sections.append(part_page_from_text(
        'Parte V', 'La pasión y el sujeto',
        marker_key='parte-v', markers=markers, counted=True,
    ))
    sections.append(chapter_piece(root, '23', 'cap-15', markers))

    sections.append(render_piece(root, '25', 'warning-page'))
    sections.append(appendix_piece(root, '26', 'ap-a', markers))
    sections.append(appendix_piece(root, '27', 'ap-b', markers))
    sections.append(appendix_piece(root, '28', 'ap-c', markers))
    sections.append(render_piece(root, '29', 'glossary', 'glosario', markers))
    sections.append(f'<section class="cover-page"><img src="{back}"></section>')

    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f'<style>{CSS}</style></head><body>{header}'
        + ''.join(sections)
        + '</body></html>'
    )

def render_pdf(
    root: Path,
    output: Path,
    toc_numbers: dict[str, str] | None = None,
    *,
    markers: bool = False,
) -> None:
    HTML(
        string=document_html(root, toc_numbers, markers=markers),
        base_url=str(root),
    ).write_pdf(str(output), presentational_hints=True)

def marker_pages(pdf_path: Path) -> dict[str, int]:
    reader = PdfReader(str(pdf_path))
    found: dict[str, int] = {}
    for page_no, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ''
        for key, _, _ in TOC_ENTRIES:
            if key in found:
                continue
            if f'[[IDX:{key}]]' in text:
                found[key] = page_no
    missing = [key for key, _, _ in TOC_ENTRIES if key not in found]
    if missing:
        raise RuntimeError(f'No fue posible localizar marcadores del índice: {missing}')
    return found

def compute_toc_numbers(pages: dict[str, int]) -> dict[str, str]:
    body_start = pages['cap-1']
    result: dict[str, str] = {}
    for key, _, kind in TOC_ENTRIES:
        physical = pages[key]
        if kind == 'front':
            result[key] = roman(physical)
        elif key == 'parte-i':
            result[key] = '1'
        else:
            result[key] = str(physical - body_start + 1)
    return result

def build(root: Path, output: Path):
    ensure_seal(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    pass1 = output.with_name(output.stem + '.pass1.pdf')
    pass2 = output.with_name(output.stem + '.pass2.pdf')

    render_pdf(root, pass1, None, markers=True)
    numbers1 = compute_toc_numbers(marker_pages(pass1))

    render_pdf(root, pass2, numbers1, markers=True)
    numbers2 = compute_toc_numbers(marker_pages(pass2))

    render_pdf(root, output, numbers2, markers=False)

    pass1.unlink(missing_ok=True)
    pass2.unlink(missing_ok=True)
    print(output)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    p.add_argument('--output', default='afrodita-areia/sobre-la-pasion/build/afrodita-areia-vol-i-sobre-la-pasion.pdf')
    a = p.parse_args()
    build(Path(a.root).resolve(), Path(a.output).resolve())

if __name__ == '__main__':
    main()
