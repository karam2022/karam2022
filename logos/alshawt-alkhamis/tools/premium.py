"""Round 2 — premium / artsy concepts for الشوط الخامس. Text is HarfBuzz-shaped outlines."""
import math, os, sys
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from shape import text_path, P, _load, feats

NAME = "الشوط الخامس"
TAG = "حكايات الكرة كما لم تُروَ"


def width_at(text, font, size):
    b = text_path(text, font, 100)[1]
    return (b[2] - b[0]) * size / 100


def size_for(text, font, width):
    b = text_path(text, font, 100)[1]
    return 100 * width / (b[2] - b[0])


def centred(text, font, width, cx, baseline, attrs):
    s = size_for(text, font, width)
    d, bb = text_path(text, font, s, cx, baseline)
    dx = cx - (bb[0] + bb[2]) / 2
    return f'<g transform="translate({dx:.2f} 0)">{P(d, attrs)}</g>', bb


def right(text, font, width, x, baseline, attrs):
    s = size_for(text, font, width)
    d, bb = text_path(text, font, s, x, baseline, "end")
    return f'<g transform="translate({x - bb[2]:.2f} 0)">{P(d, attrs)}</g>', bb


def arc_text(text, font, size, cx, cy, r, attrs, centre_deg=0):
    """Glyphs set clockwise along a circle, centred on centre_deg (0 = top)."""
    tt, hf = _load(font)
    s = size / tt["head"].unitsPerEm
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(hf, buf, feats(font))
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    total = sum(p.x_advance for p in buf.glyph_positions) * s
    out, pen_x = [], 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        theta = centre_deg + math.degrees((pen_x - total / 2) / r)
        pen = SVGPathPen(gs)
        gs[order[info.codepoint]].draw(TransformPen(pen, (s, 0, 0, -s, pos.x_offset * s, -pos.y_offset * s)))
        if pen.getCommands():
            out.append(f'<path d="{pen.getCommands()}" transform="translate({cx} {cy}) rotate({theta:.3f}) translate(0 {-r})" {attrs}/>')
        pen_x += pos.x_advance * s
    return "".join(out)


def svg(w, h, bg, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>')


# ── 1. Crest: a club badge for a club that doesn't exist ─────────────────────
CREST = {
    "dark":  dict(bg="#0E2A1F", ink="#EFE6D2", gold="#C8A24A", red="#C63A2E"),
    "light": dict(bg="#EFE6D2", ink="#0E2A1F", gold="#9C7A2C", red="#B8302A"),
}
def crest(t):
    cx, cy = 470, 160
    ring = arc_text(TAG, "kufi", 21, cx, cy, 104, f'fill="{t["gold"]}"')
    five_s = 150
    fd, fb = text_path("٥", "ruqaa", five_s, 0, 0)
    fdx, fdy = cx - (fb[0] + fb[2]) / 2, cy - (fb[1] + fb[3]) / 2
    dots = "".join(
        f'<circle cx="{cx + 104*math.sin(math.radians(a))+0:.1f}" cy="{cy - 104*math.cos(math.radians(a))+(-6):.1f}" r="4.5" '
        f'fill="{t["red"] if i == 4 else t["gold"]}"/>'
        for i, a in enumerate(range(150, 211, 15)))
    name, nb = right(NAME, "kufi", 290, 320, 170, f'fill="{t["ink"]}"')
    tag, _ = right("قناة كرة القدم", "kufi4", 120, 320, 214, f'fill="{t["gold"]}"')
    return svg(620, 320, t["bg"], f'''
<circle cx="{cx}" cy="{cy}" r="136" fill="none" stroke="{t["gold"]}" stroke-width="3"/>
<circle cx="{cx}" cy="{cy}" r="128" fill="none" stroke="{t["gold"]}" stroke-width="1"/>
<circle cx="{cx}" cy="{cy}" r="78" fill="none" stroke="{t["gold"]}" stroke-width="1.5"/>
<line x1="{cx}" y1="{cy-78}" x2="{cx}" y2="{cy+78}" stroke="{t["gold"]}" stroke-width="1.5"/>
{ring}{dots}
<g transform="translate({fdx:.2f} {fdy:.2f})">{P(fd, f'fill="{t["ink"]}"')}</g>
{name}
<rect x="{320-120}" y="190" width="120" height="2" fill="{t["gold"]}"/>
{tag}''')


# ── 2. Kashida: the calligraphic stretch becomes the halfway line ───────────
def kashida(t):
    text = "الشـــــوط الخـــــامس"
    s = size_for(text, "kufi", 520)
    d, bb = text_path(text, "kufi", s, 300, 170)
    dx = 300 - (bb[0] + bb[2]) / 2
    # locate the tatweel run in ‘الخـــــامس’ to drop the centre spot on it
    tt, hf = _load("kufi"); u = tt["head"].unitsPerEm; k = s / u
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(hf, buf, feats("kufi"))
    order = tt.getGlyphOrder(); total = sum(p.x_advance for p in buf.glyph_positions)
    x = 300 - total * k / 2 + dx; runs = []; cur = None
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = order[info.codepoint]
        if "tatweel" in g.lower() or "kashida" in g.lower():
            cur = [x, x + pos.x_advance * k] if cur is None else [cur[0], x + pos.x_advance * k]
        elif cur:
            runs.append(cur); cur = None
        x += pos.x_advance * k
    if cur: runs.append(cur)
    tat = text_path("ـ", "kufi", s, 0, 170)[1]
    ky = (tat[1] + tat[3]) / 2
    spot = ""
    if runs:
        a, b = runs[0]  # visual-left run belongs to الخامس
        mx = (a + b) / 2
        spot = (f'<circle cx="{mx:.1f}" cy="{ky:.1f}" r="{(tat[3]-tat[1])*1.9:.1f}" fill="none" stroke="{t["gold"]}" stroke-width="3"/>'
                f'<circle cx="{mx:.1f}" cy="{ky:.1f}" r="{(tat[3]-tat[1])*0.55:.1f}" fill="{t["red"]}"/>')
    tag, _ = centred(TAG, "kufi4", 250, 300, 250, f'fill="{t["gold"]}"')
    return svg(600, 300, t["bg"], f'''
<g transform="translate({dx:.2f} 0)">{P(text_path(text, "kufi", s, 300, 170)[0], f'fill="{t["ink"]}"')}</g>
{spot}
<rect x="270" y="212" width="60" height="1.5" fill="{t["gold"]}"/>
{tag}''')


# ── 3. Five Halves: Bauhaus / riso — four halves make a match, the fifth is ours
HALVES = {
    "light": dict(bg="#F1EBDD", ink="#1E2A44", a="#1F8A70", b="#1E2A44", red="#E8483A", muted="#5B6476", blend="multiply"),
    "dark":  dict(bg="#1E2A44", ink="#F1EBDD", a="#2BA383", b="#8FA3C7", red="#F0584A", muted="#B8C0D0", blend="screen"),
}
def half(cx, cy, r, rot, fill, blend):
    return (f'<path d="M{-r} 0 A{r} {r} 0 0 1 {r} 0 Z" fill="{fill}" style="mix-blend-mode:{blend}" '
            f'transform="translate({cx} {cy}) rotate({rot})"/>')
def five_halves(t):
    r, y = 36, 120
    def disc(cx, right_fill, left_fill):
        return half(cx, y, r, 90, right_fill, "normal") + half(cx, y, r, -90, left_fill, "normal")
    # read right-to-left: two full circles (4 halves), then a fifth half on its own
    icon = (disc(568, t["a"], t["b"]) + disc(488, t["a"], t["b"]) + half(408, y, r, 90, t["red"], "normal")
            + f'<path d="M408 {y-r} A{r} {r} 0 0 0 408 {y+r}" fill="none" stroke="{t["muted"]}" stroke-width="2" stroke-dasharray="5 5"/>')
    name, _ = right(NAME, "lalezar", 270, 340, 140, f'fill="{t["ink"]}"')
    tag, _ = right(TAG, "kufi4", 190, 340, 184, f'fill="{t["muted"]}"')
    return svg(640, 240, t["bg"], f'{icon}{name}{tag}')


# ── 4. Extra Time: Swiss clock — four quarters close the ring, the fifth escapes
SWISS = {
    "light": dict(bg="#F6F3EE", ink="#111111", red="#D23B2F", muted="#7A7368"),
    "dark":  dict(bg="#0F0F0F", ink="#F6F3EE", red="#E5483B", muted="#9C958A"),
}
def arc(cx, cy, r, a0, a1):
    p = lambda a, rr: (cx + rr * math.sin(math.radians(a)), cy - rr * math.cos(math.radians(a)))
    (x0, y0), (x1, y1) = p(a0, r), p(a1, r)
    return f'M{x0:.2f} {y0:.2f} A{r} {r} 0 {1 if a1-a0>180 else 0} 1 {x1:.2f} {y1:.2f}'
def spiral(cx, cy, r0, r1, a0, a1, n=40):
    pts = []
    for i in range(n + 1):
        f = i / n; a = math.radians(a0 + (a1 - a0) * f); rr = r0 + (r1 - r0) * f
        pts.append(f'{cx + rr*math.sin(a):.2f} {cy - rr*math.cos(a):.2f}')
    return "M" + " L".join(pts)
def extra_time(t):
    cx, cy, r = 490, 120, 62
    quarters = "".join(f'<path d="{arc(cx, cy, r, q*90+6, q*90+84)}" fill="none" stroke="{t["ink"]}" stroke-width="12" stroke-linecap="butt"/>' for q in range(4))
    fifth = f'<path d="{spiral(cx, cy, r+20, r+34, 6, 120)}" fill="none" stroke="{t["red"]}" stroke-width="12" stroke-linecap="round"/>'
    hand = f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy-38}" stroke="{t["ink"]}" stroke-width="5" stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="7" fill="{t["red"]}"/>'
    name, _ = right(NAME, "kufi4", 300, 360, 132, f'fill="{t["ink"]}"')
    tag, _ = right(TAG, "kufi4", 170, 360, 176, f'fill="{t["muted"]}"')
    return svg(620, 240, t["bg"], f'{quarters}{fifth}{hand}{name}<rect x="190" y="150" width="170" height="1.5" fill="{t["red"]}"/>{tag}')


# ── 5. Ensō: brush circle left open — the game that never ends ───────────────
INK = {
    "light": dict(bg="#F3EADB", ink="#1C1A17", red="#B8302A", muted="#6B5A4A"),
    "dark":  dict(bg="#16130F", ink="#F3EADB", red="#D9443A", muted="#B9A893"),
}
def enso_path(cx, cy, r, a0=-50, a1=275, n=160):
    outer, inner = [], []
    for i in range(n + 1):
        f = i / n; a = math.radians(a0 + (a1 - a0) * f)
        w = 3 + 15 * math.sin(math.pi * f ** 0.7) * (1 - 0.35 * f) + 1.6 * math.sin(f * 37)  # brush pressure + bristle wobble
        ro, ri = r + w / 2, r - w / 2
        outer.append((cx + ro * math.cos(a), cy + ro * math.sin(a)))
        inner.append((cx + ri * math.cos(a), cy + ri * math.sin(a)))
    pts = outer + inner[::-1]
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"
def enso(t):
    cx, cy = 480, 150
    fd, fb = text_path("٥", "ruqaa", 190, 0, 0)
    fdx, fdy = cx - (fb[0] + fb[2]) / 2, cy - (fb[1] + fb[3]) / 2
    name, nb = right(NAME, "ruqaa", 300, 355, 168, f'fill="{t["ink"]}"')
    tag, _ = right(TAG, "ruqaa", 190, 355, 232, f'fill="{t["muted"]}"')
    return svg(620, 300, t["bg"], f'''
<path d="{enso_path(cx, cy, 92)}" fill="{t["ink"]}"/>
<g transform="translate({fdx:.2f} {fdy:.2f})">{P(fd, f'fill="{t["red"]}"')}</g>
{name}{tag}''')


CONCEPTS = [
    ("crest", "الشعار · The Crest", "Premium",
     "A club badge for a club that doesn't exist. Tagline set around the ring, a calligraphic ٥ in the centre circle, and five dots at the bottom with the fifth in red. Gold on pitch-green.",
     crest, CREST, ("dark", "light")),
    ("kashida", "الكشيدة · Kashida", "Premium / typographic",
     "Arabic calligraphy's own stretch (ـــــ) becomes the halfway line, with the centre spot sitting on it. Wordmark only, no icon. Something only Arabic script can do.",
     kashida, CREST, ("dark", "light")),
    ("five-halves", "خمسة أنصاف · Five Halves", "Artsy / Bauhaus-riso",
     "Literal halves, read right to left: two full circles are four halves (the 90 minutes plus extra time), then a fifth red half on its own, its partner only dotted in. Flat Bauhaus colour.",
     five_halves, HALVES, ("light", "dark")),
    ("extra-time", "الوقت الإضافي · Extra Time", "Swiss minimal",
     "A match clock: four quarter arcs close the ring and the fifth breaks out of it and keeps going. Light, quiet type with a lot of space.",
     extra_time, SWISS, ("light", "dark")),
    ("enso", "الإنسو · Ensō", "Artsy / ink",
     "A brush circle left unfinished (the Zen ensō) around a Ruqaa ٥ in red. Hand-made, documentary, storytelling feel.",
     enso, INK, ("light", "dark")),
]

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for slug, _, _, _, fn, pal, themes in CONCEPTS:
        for th in themes:
            open(f"{out}/{slug}-{th}.svg", "w").write(fn(pal[th]))
    cards = "".join(f'''
<article><div class="meta"><h2>{i+1}. {title}</h2><span>{kind}</span></div><p>{desc}</p>
<div class="pair"><img src="{slug}-{th[0]}.svg" alt="{title}"><img src="{slug}-{th[1]}.svg" alt="{title}, alternate"></div></article>'''
        for i, (slug, title, kind, desc, _, _, th) in enumerate(CONCEPTS))
    open(f"{out}/preview.html", "w").write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>الشوط الخامس — Round 2</title>
<style>
body{{margin:0;padding:32px 16px;font-family:system-ui,sans-serif;background:#E7E2D8;color:#1C1A17}}
header,main{{max-width:1240px;margin:0 auto}} header{{margin-bottom:24px}} h1{{margin:0 0 4px;font-size:26px}} header p{{margin:0;color:#6B5A4A}}
main{{display:grid;grid-template-columns:1fr;gap:20px}}
article{{background:#fff;border-radius:14px;padding:18px}} .meta{{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}}
h2{{margin:0;font-size:18px}} .meta span{{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#9C7A2C}}
article p{{margin:4px 0 12px;color:#57534e;font-size:14px;max-width:70ch}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:10px}} .pair img{{width:100%;height:auto;border-radius:8px;display:block}}
@media(max-width:640px){{.pair{{grid-template-columns:1fr}}}}
</style></head><body><header><h1>الشوط الخامس · Round 2: premium &amp; artsy</h1>
<p>Five directions, made with the LogoLoom workflow. All Arabic is shaped with HarfBuzz and converted to vector outlines.</p></header>
<main>{cards}</main></body></html>''')
    print("ok")
