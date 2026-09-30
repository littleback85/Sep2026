"""Assemble fig5_document.pdf: figure + legend, figure notes, section draft, editorial answers.

Text lives in text/*.html fragments; the figure is embedded as vector SVG and the page is
printed to PDF with the pre-installed Chromium.
"""
import os
import re

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def frag(name):
    with open(os.path.join(HERE, "text", name)) as fh:
        return fh.read()


svg = open(os.path.join(OUT, "fig5.svg")).read()
svg = svg[svg.index("<svg"):]
svg = re.sub(r'width="[\d.]+pt" height="[\d.]+pt"', 'width="183mm" height="162mm"', svg, count=1)

CSS = """
@page { size: A4; margin: 14mm 13.5mm 14mm 13.5mm; }
body { font-family: Arial, 'Liberation Sans', Helvetica, sans-serif; font-size: 8.6pt;
       line-height: 1.38; color: #111; margin: 0; }
h1 { font-size: 13pt; margin: 0 0 1.5mm 0; }
h2 { font-size: 10.5pt; margin: 5mm 0 1.5mm 0; }
h3 { font-size: 9pt; margin: 3.5mm 0 1mm 0; break-after: avoid; }
h2 { break-after: avoid; }
p { margin: 0 0 2mm 0; text-align: left; }
.fig { width: 183mm; margin: 0 0 3mm 0; }
.legend { font-size: 7.4pt; line-height: 1.32; }
.legend b.t { font-size: 7.8pt; }
.page { page-break-after: always; }
.note { color: #555; font-size: 7.6pt; }
table { border-collapse: collapse; width: 100%; font-size: 7.8pt; margin: 1mm 0 3mm 0; }
td, th { border-top: 0.5pt solid #bbb; padding: 1.1mm 1.5mm; vertical-align: top; text-align: left; }
th { border-top: 0.8pt solid #333; font-weight: bold; }
tr:last-child td { border-bottom: 0.8pt solid #333; }
.flag { color: #B34700; font-weight: bold; }
.eq { text-align: center; margin: 2mm 0 2.5mm 0; font-size: 9pt; }
ol, ul { margin: 0 0 2mm 5mm; padding-left: 3mm; }
li { margin-bottom: 1mm; }
.ph { background: #FFF1E0; padding: 0 0.6mm; }
"""

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
<div class="fig">{svg}</div>
<div class="legend">{frag('legend.html')}</div>
</div>
<div class="page">{frag('notes.html')}</div>
<div class="page">{frag('section5.html')}</div>
<div>{frag('answers.html')}</div>
</body></html>"""

chrome = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=chrome if os.path.exists(chrome) else None)
    pg = b.new_page()
    pg.set_content(html, wait_until="load")
    pg.pdf(path=os.path.join(OUT, "fig5_document.pdf"), format="A4", prefer_css_page_size=True,
           print_background=True)
    b.close()
print("written", os.path.join(OUT, "fig5_document.pdf"))
