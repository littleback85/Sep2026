import math
from xml.sax.saxutils import escape

INK = "#1f2933"
MUTED = "#52606d"
UV = "#7c3aed"
VIS = "#ea8a00"
CO = "#ec4899"
AZO = "#6b7280"
AZOHEAD = "#eab308"
WATER = "#e0f2fe"
BLUE = "#2563eb"
RED = "#dc2626"
GREEN = "#059669"
CORE = "#facc15"
RAY = "#16a34a"

FONT = "'WenQuanYi Zen Hei','Noto Sans CJK SC','PingFang SC','Microsoft YaHei',sans-serif"

MARKERS = {
    "k": INK, "b": BLUE, "r": RED, "g": GREEN, "p": UV, "o": VIS, "m": MUTED, "lb": "#60a5fa",
}


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = []
        self.title = title

    def add(self, s):
        self.parts.append(s)

    def render(self):
        defs = []
        for k, c in MARKERS.items():
            defs.append(
                f'<marker id="ah-{k}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5.5" '
                f'markerHeight="5.5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
            )
        defs.append(
            '<radialGradient id="haloSrc"><stop offset="0" stop-color="#f472b6" stop-opacity="0.55"/>'
            '<stop offset="1" stop-color="#f472b6" stop-opacity="0"/></radialGradient>'
        )
        defs.append(
            '<radialGradient id="warm"><stop offset="0" stop-color="#f87171" stop-opacity="0.6"/>'
            '<stop offset="1" stop-color="#f87171" stop-opacity="0"/></radialGradient>'
        )
        defs.append(
            '<radialGradient id="glow"><stop offset="0" stop-color="#fde047" stop-opacity="0.8"/>'
            '<stop offset="1" stop-color="#fde047" stop-opacity="0"/></radialGradient>'
        )
        style = (
            f"text{{font-family:{FONT};fill:{INK};}}"
            ".h{font-weight:700;} .mut{fill:#52606d;} .halo{paint-order:stroke;stroke:#ffffff;stroke-width:4px;stroke-linejoin:round;}"
        )
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" font-family="{FONT}">'
            f"<title>{escape(self.title)}</title><style>{style}</style><defs>{''.join(defs)}</defs>"
            f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="#ffffff"/>'
        )
        return head + "\n".join(self.parts) + "</svg>"

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.render())

    # ---------- primitives ----------
    def text(self, x, y, s, size=13, anchor="start", bold=False, color=None, italic=False, halo=False):
        attrs = f'x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}"'
        if halo:
            attrs += ' class="halo"'
        if bold:
            attrs += ' font-weight="700"'
        if color:
            attrs += f' fill="{color}"'
        if italic:
            attrs += ' font-style="italic"'
        self.add(f"<text {attrs}>{escape(s)}</text>")

    def lines(self, x, y, arr, size=12, lh=None, anchor="start", color=None, bold=False):
        lh = lh or size * 1.45
        for i, s in enumerate(arr):
            self.text(x, y + i * lh, s, size, anchor, bold, color)

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1.2, rx=6, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o}/>')

    def line(self, x1, y1, x2, y2, color=INK, sw=1.5, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}{o}/>')

    def arrow(self, x1, y1, x2, y2, m="k", sw=2.4, dash=None, opacity=None):
        c = MARKERS[m]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}" marker-end="url(#ah-{m})"{d}{o}/>')

    def path(self, d, stroke=INK, sw=1.5, fill="none", m=None, dash=None, opacity=None):
        me = f' marker-end="url(#ah-{m})"' if m else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{me}{da}{o}/>')

    def circle(self, x, y, r, fill="none", stroke=INK, sw=1.2, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o}/>')

    def poly(self, pts, fill, stroke="none", sw=1, opacity=None):
        p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{o}/>')

    # ---------- domain glyphs ----------
    def aster(self, x, y, s=1.0, opacity=1.0, rays=18, core=10, ray_len=26, color=RAY):
        g = [f'<g opacity="{opacity}">']
        for i in range(rays):
            a = 2 * math.pi * i / rays + 0.13
            L = ray_len * (1.0 if i % 2 == 0 else 0.78)
            bend = 0.18 if i % 3 else -0.15
            x1, y1 = x + core * 0.8 * s * math.cos(a), y + core * 0.8 * s * math.sin(a)
            x2, y2 = x + (core + L) * s * math.cos(a), y + (core + L) * s * math.sin(a)
            mx = x + (core + L * 0.55) * s * math.cos(a + bend)
            my = y + (core + L * 0.55) * s * math.sin(a + bend)
            g.append(f'<path d="M{x1:.1f},{y1:.1f} Q{mx:.1f},{my:.1f} {x2:.1f},{y2:.1f}" stroke="{color}" stroke-width="{max(1.2, 2.0*s):.2f}" fill="none" stroke-linecap="round"/>')
        g.append(f'<circle cx="{x}" cy="{y}" r="{core*s:.1f}" fill="{CORE}" stroke="#ca8a04" stroke-width="1"/>')
        g.append("</g>")
        self.add("".join(g))

    def co(self, x, y, r=4.5):
        self.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{CO}" stroke="#9d174d" stroke-width="0.8"/>')

    def azo(self, x, y, rot=0, s=1.0):
        self.add(
            f'<g transform="translate({x},{y}) rotate({rot}) scale({s})">'
            f'<polyline points="-8,4 -2,-3 4,3 9,-4" fill="none" stroke="{AZO}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="9" cy="-4" r="2.8" fill="{AZOHEAD}" stroke="#a16207" stroke-width="0.6"/></g>'
        )

    def lamp_h(self, x, y, color, direction=1):
        """Horizontal flashlight; (x,y) = centre of lens; direction=1 shines to the right."""
        bx = x - 44 if direction == 1 else x + 4
        self.add(f'<rect x="{bx}" y="{y-11}" width="40" height="22" rx="4" fill="#4b5563"/>')
        self.add(f'<ellipse cx="{x}" cy="{y}" rx="5" ry="12" fill="{color}"/>')

    def lamp_v(self, x, y, color):
        """Vertical lamp pointing down; (x,y) = centre of lens."""
        self.add(f'<rect x="{x-12}" y="{y-34}" width="24" height="30" rx="4" fill="#4b5563"/>')
        self.add(f'<ellipse cx="{x}" cy="{y}" rx="13" ry="5" fill="{color}"/>')

    def box(self, x, y, w, h, lines_, fill="#f8fafc", stroke="#94a3b8", size=12, color=None, bold_first=False):
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.2, rx=8)
        lh = size * 1.4
        total = lh * (len(lines_) - 1)
        y0 = y + h / 2 - total / 2 + size * 0.36
        for i, s in enumerate(lines_):
            self.text(x + w / 2, y0 + i * lh, s, size, "middle", bold=(bold_first and i == 0), color=color)
