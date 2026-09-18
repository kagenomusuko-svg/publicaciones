#!/usr/bin/env python3
from __future__ import annotations

import argparse, base64, html, io, re
from pathlib import Path
from markdown_it import MarkdownIt
from PIL import Image
from weasyprint import HTML

GREEN = '#1E4C45'
TEXT = '#262626'
MUTED = '#666666'
RULE = '#D8D8D8'
PUBLISHER = 'Centro Multidisciplinario Meriadock Formación y Asesoría A.C.'
MOTTO = 'La fuerza interior nos impulsa, un pequeño apoyo de los demás nos bendice'

CSS = r'''
@page { size: A4; }
@page cover { margin: 0; }
@page title { margin: 0; }
@page legal { margin: 22mm 23mm; }
@page epigraph { margin: 0; }
@page part { margin: 0; }
@page front {
  margin: 27.5mm 20.5mm 22mm;
  @top-center { content: element(bookheader); }
  @bottom-left { content: "Centro Multidisciplinario Meriadock Formación y Asesoría A.C."; font: 7.2pt "EB Garamond"; color: #666; border-top: .5pt solid #D8D8D8; padding-top: 2mm; }
  @bottom-right { content: counter(page, upper-roman); font: 7.2pt "EB Garamond"; color: #666; border-top: .5pt solid #D8D8D8; padding-top: 2mm; }
}
@page body {
  margin: 27.5mm 20.5mm 22mm;
  @top-center { content: element(bookheader); }
  @bottom-left { content: "Centro Multidisciplinario Meriadock Formación y Asesoría A.C."; font: 7.2pt "EB Garamond"; color: #666; border-top: .5pt solid #D8D8D8; padding-top: 2mm; }
  @bottom-right { content: counter(page); font: 7.2pt "EB Garamond"; color: #666; border-top: .5pt solid #D8D8D8; padding-top: 2mm; }
}
html, body { margin: 0; padding: 0; font-family: "EB Garamond", Garamond, serif; color: #262626; }
.running-header { position: running(bookheader); width: 169mm; height: 13mm; display: flex; align-items: center; border-bottom: .6pt solid #CFCFCF; padding-bottom: 2mm; }
.running-header img { width: 8mm; height: 8mm; object-fit: contain; margin-right: 3mm; }
.running-header .book { font: 700 8pt "EB Garamond"; color: #1E4C45; letter-spacing: .04em; }
.running-header .sub { margin-left: auto; font: 7.5pt "EB Garamond"; color: #666; }
.cover-page { page: cover; break-after: page; width: 210mm; height: 297mm; }
.cover-page img { width: 210mm; height: 297mm; object-fit: fill; display: block; }
.title-page { page: title; break-after: page; height: 297mm; box-sizing: border-box; text-align: center; padding: 24mm 20mm 22mm; position: relative; }
.title-page .seal { width: 34mm; height: 34mm; object-fit: contain; }
.title-page .institution { margin-top: 5mm; color: #1E4C45; font: 600 13pt "EB Garamond"; letter-spacing: .07em; text-transform: uppercase; }
.title-page .rule { width: 70mm; margin: 3mm auto 2mm; border-top: .7pt solid #1E4C45; }
.title-page .org { color: #666; font-size: 9.5pt; }
.title-page .motto { color: #1E4C45; font-size: 8.5pt; font-style: italic; margin-top: 2.5mm; }
.title-page .main { margin-top: 33mm; font-size: 31pt; font-weight: 700; letter-spacing: .02em; }
.title-page .subtitle { margin-top: 6mm; color: #1E4C45; font-size: 21pt; font-style: italic; }
.title-page .volume { color: #666; font-size: 11pt; margin-top: 3mm; }
.title-page .author { margin-top: 26mm; font-size: 16pt; }
.title-page .bottom { position: absolute; left: 20mm; right: 20mm; bottom: 20mm; color: #666; font-size: 9.5pt; line-height: 1.5; }
.title-page .collection { font-style: italic; }
.legal-page { page: legal; break-after: page; font-size: 9pt; line-height: 1.45; color: #555; }
.legal-page h1, .legal-page h2 { color: #262626; font-size: 15pt; margin: 0 0 8mm; }
.epigraph-page { page: epigraph; break-after: page; height: 297mm; display: flex; align-items: center; justify-content: center; text-align: center; padding: 0 45mm; box-sizing: border-box; }
.epigraph-page blockquote { border: 0; margin: 0; color: #444; font-size: 14pt; line-height: 1.5; font-style: italic; }
.frontmatter { page: front; break-before: page; }
.part-page { page: part; break-before: page; break-after: page; height: 297mm; box-sizing: border-box; text-align: center; padding-top: 62mm; }
.part-page img { width: 28mm; height: 28mm; object-fit: contain; }
.part-page .series { margin-top: 5mm; color: #1E4C45; font-size: 14pt; font-variant: small-caps; letter-spacing: .08em; }
.part-page .rule { width: 75mm; border-top: .7pt solid #1E4C45; margin: 5mm auto 14mm; }
.part-page h1 { font-size: 27pt; margin: 0; }
.part-page h2 { font-size: 17pt; color: #262626; font-weight: 400; margin-top: 5mm; }
.part-page .epigraph { margin-top: 8mm; color: #666; font-size: 11pt; font-style: italic; }
.chapter, .appendix, .glossary, .warning-page { page: body; break-before: page; }
.body-start { counter-reset: page 0; }
.frontmatter, .chapter, .appendix, .glossary, .warning-page { font-size: 10.5pt; line-height: 1.33; }
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
.chapter > blockquote:first-of-type { max-width: 120mm; margin: 6mm auto 9mm; }
table { width: 100%; border-collapse: collapse; font-size: 9pt; margin: 5mm 0; }
th, td { border: .5pt solid #D8D8D8; padding: 2mm; vertical-align: top; }
th { background: #F5F5F2; }
'''

md = MarkdownIt('commonmark', {'html': True}).enable('table')

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
    year_match = re.search(r'(20\\d{2})', publisher)
    year = year_match.group(1) if year_match else '2026'
    publisher = publisher.replace(' · 2026', '').strip()
    esc = html.escape
    return f'''<section class="title-page"><img class="seal" src="assets/logo-green.png"><div class="institution">Centro Multidisciplinario Meriadock</div><div class="rule"></div><div class="org">Formación y Asesoría A.C.</div><div class="motto">“{esc(MOTTO)}”</div><div class="main">{esc(title.upper())}</div><div class="subtitle">{esc(subtitle)}</div><div class="volume">{esc(volume)}</div><div class="author">{esc(author)}</div><div class="bottom"><div class="collection">{esc(collection)}</div><div>{esc(publisher.replace(' ·','').strip())}</div><div>{esc(year)}</div></div></section>'''

def epigraph(root: Path) -> str:
    return '<section class="epigraph-page">' + md.render((root/'03.md').read_text(encoding='utf-8')) + '</section>'

def part_page_from_text(part: str, subtitle: str, epigraph: str = '') -> str:
    return f'''<section class="part-page"><img src="assets/logo-green.png"><div class="series">AFRODITA AREIA · I</div><div class="rule"></div><h1>{html.escape(part)}</h1><h2>{html.escape(subtitle)}</h2><div class="epigraph">{html.escape(epigraph)}</div></section>'''

def part_page(root: Path) -> str:
    lines = clean_lines((root/'08.md').read_text(encoding='utf-8'))
    return part_page_from_text(
        lines[0] if lines else 'Parte I',
        lines[1] if len(lines) > 1 else '',
        lines[2] if len(lines) > 2 else '',
    )

def strip_part_marker(raw: str) -> str:
    return re.sub(r'^\s*\*Parte\s+[IVXLCDM]+\s+[—-]\s+[^*]+\*\s*\n+', '', raw, count=1, flags=re.I)

def chapter_piece(root: Path, stem: str, first: bool = False) -> str:
    raw = strip_part_marker((root/f'{stem}.md').read_text(encoding='utf-8'))
    cls = 'chapter body-start' if first else 'chapter'
    return f'<section class="{cls}">' + md.render(raw) + '</section>'

def appendix_piece(root: Path, stem: str) -> str:
    return f'<section class="appendix">' + md.render((root/f'{stem}.md').read_text(encoding='utf-8')) + '</section>'

def render_piece(root: Path, stem: str, cls: str) -> str:
    return f'<section class="{cls}">' + md.render((root/f'{stem}.md').read_text(encoding='utf-8')) + '</section>'

def build(root: Path, output: Path):
    ensure_seal(root)
    cover = html.escape((root/'Portada Vol I.png').as_uri())
    back = html.escape((root/'Contraportada Vol I.png').as_uri())
    header = '''<header class="running-header"><img src="assets/logo-green.png"><span class="book">AFRODITA AREIA · I</span><span class="sub">SOBRE LA PASIÓN</span></header>'''

    sections = [
        f'<section class="cover-page"><img src="{cover}"></section>',
        title_page(root),
        render_piece(root, '02', 'legal-page'),
        epigraph(root),
    ]

    for stem in ('04', '05', '06', '07'):
        sections.append(render_piece(root, stem, 'frontmatter'))

    sections.append(part_page(root))
    sections.append(chapter_piece(root, '09', first=True))
    sections.append(chapter_piece(root, '10'))
    sections.append(chapter_piece(root, '11'))

    sections.append(part_page_from_text('Parte II', 'La pasión como fuerza ontológica'))
    for stem in ('12', '13', '14', '15', '16', '17'):
        sections.append(chapter_piece(root, stem))

    sections.append(part_page_from_text('Parte III', 'Las mediaciones'))
    for stem in ('18', '19'):
        sections.append(chapter_piece(root, stem))

    sections.append(part_page_from_text('Parte IV', 'El ego como integral'))
    for stem in ('20', '21', '22'):
        sections.append(chapter_piece(root, stem))

    sections.append(part_page_from_text('Parte V', 'La pasión y el sujeto'))
    sections.append(chapter_piece(root, '23'))

    sections.append(render_piece(root, '25', 'warning-page'))
    for stem in ('26', '27', '28'):
        sections.append(appendix_piece(root, stem))
    sections.append(render_piece(root, '29', 'glossary'))

    sections.append(f'<section class="cover-page"><img src="{back}"></section>')

    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{header}{''.join(sections)}</body></html>'''
    output.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=doc, base_url=str(root)).write_pdf(str(output), presentational_hints=True)
    print(output)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    p.add_argument('--output', default='sobre-la-pasion/build/afrodita-areia-vol-i-sobre-la-pasion.pdf')
    a = p.parse_args()
    build(Path(a.root).resolve(), Path(a.output).resolve())

if __name__ == '__main__':
    main()
