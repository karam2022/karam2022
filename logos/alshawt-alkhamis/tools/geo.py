"""Round 5 — Arabic geometry: a football whose panels are an Islamic star pattern (girih)."""
import math, os, sys
from girih import ball
from five import lockup, wrap

STYLES = {
    # night match: brass strapwork on black, green stars, the centre star red
    "brass": dict(bg="#0F0E0C", tile="#0F0E0C", field="#141A16", star="#1F4D3A", band="#C9A45C", edge="#0F0E0C", centre="#C4352B", shade=0.55),
    # zellige: Fez tilework — cream bands, cobalt / green / ochre stars
    "zellige": dict(bg="#F1E8D8", tile="#F1E8D8", field="#1E3A6E", star=["#2F6B4A", "#C98B2B", "#1E3A6E"], band="#F4ECDD", edge="#1C2430", centre="#C4352B", shade=0.35),
    # minimal: ink lines on paper
    "line": dict(bg="#F1E8D8", tile="#F1E8D8", field="#F1E8D8", star="#F1E8D8", band="#161513", edge=None, centre="#C4352B", shade=0.0),
}


def pth(p):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in p) + "Z"


def ball_svg(st, cx=200, cy=200, r=150, theta=62, band_w=None, clip_r=None, uid="b"):
    faces = ball(cx, cy, r, theta=theta)
    band_w = band_w or r * 0.045
    clip_r = clip_r or r * 1.0
    fields, stars, bands = [], [], []
    for idx, (k, _, f, star, c, nz) in enumerate(faces):
        fields.append(f'<path d="{pth(f)}" fill="{st["field"]}" stroke="{st["field"]}" stroke-width="1"/>')
        centre = abs(c[0] - cx) < 1 and abs(c[1] - cy) < 1
        sc = st["star"]
        if isinstance(sc, list):
            sc = sc[0] if k == 5 else sc[1 + (idx % 2)]
        stars.append(f'<path d="{pth(star)}" fill="{sc}"/>')
        if centre:  # the ball's patch: only the inner pentagon, not a five-pointed star
            stars.append(f'<path d="{pth(star[1::2])}" fill="{st["centre"]}"/>')
        d = pth(star)
        if st["edge"]:
            bands.append(f'<path d="{d}" fill="none" stroke="{st["edge"]}" stroke-width="{band_w * 1.9:.2f}" stroke-linejoin="miter" stroke-miterlimit="10"/>')
        bands.append(f'<path d="{d}" fill="none" stroke="{st["band"]}" stroke-width="{band_w:.2f}" stroke-linejoin="miter" stroke-miterlimit="10"/>')
    shade = ""
    if st["shade"]:
        shade = (f'<radialGradient id="sh{uid}" cx="38%" cy="32%" r="75%"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                 f'<stop offset=".65" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="{st["shade"]}"/></radialGradient>'
                 f'<circle cx="{cx}" cy="{cy}" r="{clip_r}" fill="url(#sh{uid})"/>')
    ring = f'<circle cx="{cx}" cy="{cy}" r="{clip_r}" fill="none" stroke="{st["band"]}" stroke-width="{band_w * 0.9:.2f}"/>'
    return (f'<clipPath id="c{uid}"><circle cx="{cx}" cy="{cy}" r="{clip_r}"/></clipPath>'
            f'<g clip-path="url(#c{uid})"><circle cx="{cx}" cy="{cy}" r="{clip_r}" fill="{st["field"]}"/>{"".join(fields)}{"".join(stars)}{"".join(bands)}{shade}</g>{ring}')


def mark(style, zoom=1.0, uid="m"):
    st = STYLES[style]
    r = 150 * zoom
    return f'<rect width="400" height="400" rx="44" fill="{st["tile"]}"/>' + ball_svg(st, r=r, clip_r=150, band_w=6.5 * zoom ** 0.6, uid=uid)


NAME = "الشوط الخامس"
TAG = "حكايات الكرة كما لم تُروَ"


def lockup_on(style, uid):
    """Mark + Ruqaa wordmark + English line, coloured for the style's background."""
    from shape import text_path, P
    st = STYLES[style]
    dark = style == "brass"
    ink = "#F1E8D8" if dark else "#161513"
    accent = st["band"] if dark else "#2F6B4A"
    muted = "#B9A893" if dark else "#6B5A4A"
    nd, nb = text_path(NAME, "ruqaa", 120, 0, 0)
    e1, b1 = text_path("THE FIFTH", "mont", 34, 0, 0, "start", tracking=4)
    e2, b2 = text_path("HALF", "mont", 34, 0, 0, "start", tracking=4)
    tg, tb = text_path(TAG, "ruqaa", 30, 0, 0)
    cx, gap = 330, 30
    total = (b1[2] - b1[0]) + gap + (b2[2] - b2[0])
    x1 = cx - total / 2 - b1[0]; x2 = cx - total / 2 + (b1[2] - b1[0]) + gap - b2[0]
    return wrap(960, 380, f'''
<g transform="translate({cx - (nb[0]+nb[2])/2:.2f} 175)">{P(nd, f'fill="{ink}"')}</g>
<g transform="translate({x1:.2f} 248)">{P(e1, f'fill="{ink}"')}</g>
<g transform="translate({x2:.2f} 248)">{P(e2, f'fill="{accent}"')}</g>
<g transform="translate({cx - (tb[0]+tb[2])/2:.2f} 306)">{P(tg, f'fill="{muted}"')}</g>
<g transform="translate(640 30) scale(.8)">{ball_svg(st, r=150, clip_r=150, band_w=6.5, uid=uid)}</g>''', st["bg"])


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for s in STYLES:
        open(f"{out}/ball-{s}.svg", "w").write(wrap(400, 400, mark(s, 1.0, s)))
        open(f"{out}/ball-{s}-avatar.svg", "w").write(wrap(400, 400, mark(s, 1.9, s + "a")))
        open(f"{out}/lockup-{s}.svg", "w").write(lockup_on(s, s + "l"))
    print("ok")
