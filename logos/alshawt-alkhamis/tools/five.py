"""Round 3 — the 5 as the identity. Marks drawn from the channel's world: clock, pitch, film, newsprint, ticket."""
import math, os, sys
from shape import text_path, P

NAME = "الشوط الخامس"
TAG = "حكايات الكرة كما لم تُروَ"
C = dict(cream="#F1E8D8", paper="#E9DECB", ink="#1E1E1E", red="#B8302A", green="#2F6B4A", green2="#2A6243",
         sepia="#2B241C", film="#16130F", muted="#6B5A4A", gold="#B08D4A")


def five_geom(cx, top, h):
    """A constructed 5 (centreline): top bar, stem, open bowl. Angles in SVG space (y down)."""
    r = 0.33 * h
    c = (cx + 0.02 * h, top + h - r)
    a0, a1 = -150, 145
    pt = lambda a: (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
    s, e = pt(a0), pt(a1)
    bar_x1 = c[0] + 0.98 * r
    d = (f"M{bar_x1:.2f} {top:.2f} L{s[0]:.2f} {top:.2f} L{s[0]:.2f} {s[1]:.2f} "
         f"A{r:.2f} {r:.2f} 0 1 1 {e[0]:.2f} {e[1]:.2f}")
    return dict(d=d, c=c, r=r, top=top, stem_x=s[0], stem_y=s[1], bar_x1=bar_x1, a0=a0, a1=a1, start=s, end=e)


def dist_to_five(p, g):
    def seg(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - ax - t * dx, py - ay - t * dy)
    d1 = seg(p, (g["bar_x1"], g["top"]), (g["stem_x"], g["top"]))
    d2 = seg(p, (g["stem_x"], g["top"]), g["start"])
    th = math.degrees(math.atan2(p[1] - g["c"][1], p[0] - g["c"][0]))
    if g["a0"] <= th <= g["a1"]:
        d3 = abs(math.hypot(p[0] - g["c"][0], p[1] - g["c"][1]) - g["r"])
    else:
        d3 = min(math.hypot(p[0] - g["start"][0], p[1] - g["start"][1]), math.hypot(p[0] - g["end"][0], p[1] - g["end"][1]))
    return min(d1, d2, d3)


def centred_glyph(text, font, size, cx, cy, fill):
    d, b = text_path(text, font, size, 0, 0)
    return f'<g transform="translate({cx - (b[0]+b[2])/2:.2f} {cy - (b[1]+b[3])/2:.2f})">{P(d, f"fill=\"{fill}\"")}</g>'


def wrap(w, h, body, bg=None):
    bgr = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{bgr}{body}</svg>'


# ── 1. Stopwatch 5 — the bowl of the 5 is a referee's watch face ─────────────
def stopwatch():
    g = five_geom(195, 80, 250); sw = 34; cx, cy = g["c"]
    ticks = []
    for i in range(60):
        a = math.radians(i * 6 - 90); major = i % 5 == 0
        r0, r1 = g["r"] - sw / 2 - 7, g["r"] - sw / 2 - (19 if major else 12)
        ticks.append(f'<line x1="{cx + r0*math.cos(a):.2f}" y1="{cy + r0*math.sin(a):.2f}" x2="{cx + r1*math.cos(a):.2f}" '
                     f'y2="{cy + r1*math.sin(a):.2f}" stroke="{C["ink"]}" stroke-width="{3 if major else 1.4}"/>')
    ha = math.radians(150 - 90)  # hand on the fifth mark
    hx, hy = cx + 50 * math.cos(ha), cy + 50 * math.sin(ha)
    tx, ty = cx - 14 * math.cos(ha), cy - 14 * math.sin(ha)
    bar_mid = (g["stem_x"] + g["bar_x1"]) / 2 + 10
    return f'''
<rect width="400" height="400" rx="44" fill="{C["cream"]}"/>
<rect x="{bar_mid-13}" y="{g["top"]-sw/2-22}" width="26" height="14" rx="3" fill="{C["ink"]}"/>
<rect x="{bar_mid-5}" y="{g["top"]-sw/2-10}" width="10" height="12" fill="{C["ink"]}"/>
<path d="{g["d"]}" fill="none" stroke="{C["ink"]}" stroke-width="{sw}" stroke-linejoin="miter"/>
{"".join(ticks)}
<line x1="{tx:.2f}" y1="{ty:.2f}" x2="{hx:.2f}" y2="{hy:.2f}" stroke="{C["red"]}" stroke-width="4" stroke-linecap="round"/>
<circle cx="{cx:.2f}" cy="{cy:.2f}" r="7" fill="{C["red"]}"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r="2.5" fill="{C["cream"]}"/>'''


# ── 2. Pitch 5 — drawn only in pitch markings: corner, touchline, centre circle
def pitch():
    g = five_geom(195, 85, 240); sw = 10; cx, cy = g["c"]
    stripes = "".join(f'<rect x="0" y="{y}" width="400" height="40" fill="{C["green2"]}"/>' for y in range(0, 400, 80))
    x0, y0 = g["stem_x"], g["top"]; k = 22
    return f'''
<clipPath id="pt"><rect width="400" height="400" rx="44"/></clipPath>
<g clip-path="url(#pt)"><rect width="400" height="400" fill="{C["green"]}"/>{stripes}</g>
<path d="{g["d"]}" fill="none" stroke="{C["cream"]}" stroke-width="{sw}" stroke-linecap="square"/>
<path d="M{x0} {y0 + k} A{k} {k} 0 0 0 {x0 + k} {y0}" fill="none" stroke="{C["cream"]}" stroke-width="4"/>
<line x1="{x0}" y1="{y0}" x2="{x0 - 24}" y2="{y0 - 42}" stroke="{C["cream"]}" stroke-width="4" stroke-linecap="round"/>
<path d="M{x0 - 24} {y0 - 42} L{x0 - 2} {y0 - 40} L{x0 - 14} {y0 - 24} Z" fill="{C["red"]}"/>
<circle cx="{cx:.2f}" cy="{cy:.2f}" r="10" fill="{C["red"]}"/>'''


# ── 3. Archive Reel — a 35mm frame; the bowl of the 5 holds the Arabic ٥ ─────
def reel():
    g = five_geom(195, 108, 200); sw = 28; cx, cy = g["c"]
    holes = "".join(f'<rect x="{x}" y="{y}" width="17" height="22" rx="4" fill="{C["cream"]}" opacity=".9"/>'
                    for x in range(28, 380, 36) for y in (26, 352))
    return f'''
<defs><radialGradient id="vg" cx="50%" cy="50%" r="65%"><stop offset="0" stop-color="#40362A"/><stop offset="1" stop-color="#1B1712"/></radialGradient></defs>
<rect width="400" height="400" rx="44" fill="{C["film"]}"/>{holes}
<rect x="22" y="66" width="356" height="268" rx="6" fill="url(#vg)"/>
<path d="{g["d"]}" fill="none" stroke="{C["cream"]}" stroke-width="{sw}"/>
{centred_glyph("٥", "ruqaa", 92, cx, cy, C["red"])}'''


# ── 4. Halftone — newsprint dots; the 5 in ink over a red floodlight ─────────
def halftone():
    g = five_geom(190, 82, 250); sw = 44
    sun_c, sun_r = (292, 112), 84
    dots, step, rot = [], 9.0, math.radians(45)
    for i in range(-60, 61):
        for j in range(-60, 61):
            u, v = i * step, j * step
            x = 200 + u * math.cos(rot) - v * math.sin(rot)
            y = 200 + u * math.sin(rot) + v * math.cos(rot)
            if not (-5 < x < 405 and -5 < y < 405):
                continue
            shade = 0.35 + 0.65 * (1 - (x + (400 - y)) / 800)   # darker towards bottom-left
            if dist_to_five((x, y), g) < sw / 2:
                dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.6*shade + 0.6:.2f}" fill="{C["ink"]}"/>')
            else:
                dd = math.hypot(x - sun_c[0], y - sun_c[1])
                if dd < sun_r:
                    rr = 4.3 * (1 - (dd / sun_r) ** 2) ** 0.5 + 0.5
                    dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.2f}" fill="{C["red"]}"/>')
    return f'''
<clipPath id="ht"><rect width="400" height="400" rx="44"/></clipPath>
<rect width="400" height="400" rx="44" fill="{C["paper"]}"/><g clip-path="url(#ht)">{"".join(dots)}</g>'''


# ── 5. Ticket — a match ticket from a game that never got played ─────────────
def ticket():
    g = five_geom(532, 74, 128); sw = 22
    name_d, nb = text_path(NAME, "ruqaa", 64, 0, 0)
    en_d, eb = text_path("THE FIFTH HALF", "mont", 22, 0, 0, "start", tracking=3)
    tg_d, tb = text_path(TAG, "ruqaa", 22, 0, 0)
    no_d, nob = text_path("No. 0005", "mont5", 14, 0, 0, "start", tracking=2)
    mid = 250
    def place(d, b, cx, base):
        return f'<g transform="translate({cx - (b[0]+b[2])/2:.2f} {base})">'
    return f'''
<rect width="640" height="300" fill="#D9CCB4"/>
<rect x="24" y="36" width="592" height="228" rx="10" fill="{C["cream"]}"/>
<circle cx="470" cy="36" r="16" fill="#D9CCB4"/><circle cx="470" cy="264" r="16" fill="#D9CCB4"/>
<rect x="36" y="48" width="568" height="204" rx="6" fill="none" stroke="{C["ink"]}" stroke-width="1"/>
<line x1="470" y1="58" x2="470" y2="242" stroke="{C["ink"]}" stroke-width="2" stroke-dasharray="2 7" stroke-linecap="round"/>
{place(name_d, nb, mid, 140)}{P(name_d, f'fill="{C["ink"]}"')}</g>
{place(en_d, eb, mid, 178)}{P(en_d, f'fill="{C["green"]}"')}</g>
<rect x="{mid-60}" y="192" width="120" height="1.5" fill="{C["red"]}"/>
{place(tg_d, tb, mid, 224)}{P(tg_d, f'fill="{C["muted"]}"')}</g>
<path d="{g["d"]}" fill="none" stroke="{C["red"]}" stroke-width="{sw}"/>
{place(no_d, nob, 543, 240)}{P(no_d, f'fill="{C["ink"]}"')}</g>'''


def lockup(mark_body):
    """Banner-style lockup like his: mark on the right, Ruqaa wordmark, English line, tagline."""
    name_d, nb = text_path(NAME, "ruqaa", 120, 0, 0)
    en1, e1 = text_path("THE FIFTH", "mont", 34, 0, 0, "start", tracking=4)
    en2, e2 = text_path("HALF", "mont", 34, 0, 0, "start", tracking=4)
    tg, tb = text_path(TAG, "ruqaa", 30, 0, 0)
    gap = 30; total = (e1[2] - e1[0]) + gap + (e2[2] - e2[0]); cx = 330
    x1 = cx - total / 2 - e1[0]; x2 = cx - total / 2 + (e1[2] - e1[0]) + gap - e2[0]
    return wrap(960, 380, f'''
<g transform="translate({cx - (nb[0]+nb[2])/2:.2f} 175)">{P(name_d, f'fill="{C["ink"]}"')}</g>
<g transform="translate({x1:.2f} 248)">{P(en1, f'fill="{C["ink"]}"')}</g>
<g transform="translate({x2:.2f} 248)">{P(en2, f'fill="{C["green"]}"')}</g>
<g transform="translate({cx - (tb[0]+tb[2])/2:.2f} 306)">{P(tg, f'fill="{C["muted"]}"')}</g>
<g transform="translate(640 50) scale(.7)">{mark_body}</g>''', C["cream"])


MARKS = [
    ("stopwatch", "ساعة الحكم · Referee's Watch",
     "The bowl of the 5 is a stopwatch face, and the red hand stops on the fifth mark. It ties straight into the clock in his banner. Reads as a 5 first, as time second.", stopwatch),
    ("pitch", "الملعب · Pitch Lines",
     "A 5 drawn only in pitch markings: the corner arc and flag top-left, the touchline as the stem, the centre circle as the bowl, the centre spot in red. Monoline and premium.", pitch),
    ("reel", "شريط الأرشيف · Archive Reel",
     "A 35mm film frame. The Latin 5 holds the Arabic ٥ in its bowl, so one number appears in both scripts. Fits the 'never-told stories' documentary angle.", reel),
    ("halftone", "طباعة الجرائد · Halftone",
     "Old-newspaper halftone dots: an ink 5 printed over a red floodlight. Two-colour riso-print feel, the most artsy of the five, and still bold at avatar size.", halftone),
]

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for slug, _, _, fn in MARKS:
        body = fn()
        open(f"{out}/mark-{slug}.svg", "w").write(wrap(400, 400, body))
        open(f"{out}/lockup-{slug}.svg", "w").write(lockup(body))
    open(f"{out}/ticket.svg", "w").write(wrap(640, 300, ticket()))
    print("ok")
