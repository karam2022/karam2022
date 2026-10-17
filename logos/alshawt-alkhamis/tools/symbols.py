"""Round 4 — symbol-first marks. No letters inside the mark; one idea each."""
import math, os, sys
from five import lockup, wrap

C = dict(cream="#F1E8D8", ink="#161513", red="#C4352B", green="#2F6B4A", green2="#29603F", sand="#D9CBB2")


def pt(c, r, deg):
    a = math.radians(deg)
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def poly(pts):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + "Z"


def ray_circle(p, d, c, R):
    """First positive t where p + t·d hits circle(c, R)."""
    fx, fy = p[0] - c[0], p[1] - c[1]
    a = d[0] ** 2 + d[1] ** 2; b = 2 * (fx * d[0] + fy * d[1]); cc = fx ** 2 + fy ** 2 - R ** 2
    t = (-b + math.sqrt(b * b - 4 * a * cc)) / (2 * a)
    return (p[0] + t * d[0], p[1] + t * d[1])


# ── A. Aperture — a camera iris with five blades; the opening is a football's pentagon
def aperture():
    c, R, r = (200, 200), 138, 46
    V = [pt(c, r, -90 + 72 * i) for i in range(5)]
    P = []
    for i in range(5):
        a, b = V[i], V[(i + 1) % 5]
        P.append(ray_circle(b, (b[0] - a[0], b[1] - a[1]), c, R))
    tones = ["#E9DCC4", "#D6C3A3", "#C3AB85", "#AE9368", "#977B50"]
    blades = []
    for i in range(5):
        v = V[(i + 1) % 5]; p0, p1 = P[i], P[(i + 1) % 5]
        a0 = math.degrees(math.atan2(p0[1] - c[1], p0[0] - c[0]))
        a1 = math.degrees(math.atan2(p1[1] - c[1], p1[0] - c[0]))
        while a1 < a0: a1 += 360
        arc = [pt(c, R, a0 + (a1 - a0) * k / 24) for k in range(25)]
        blades.append(f'<path d="{poly([v] + arc)}" fill="{tones[i]}" stroke="{C["ink"]}" stroke-width="5" stroke-linejoin="round"/>')
    return f'''<rect width="400" height="400" rx="44" fill="{C["ink"]}"/>
{"".join(blades)}
<path d="{poly(V)}" fill="{C["red"]}" stroke="{C["ink"]}" stroke-width="5" stroke-linejoin="round"/>
<circle cx="200" cy="200" r="{R}" fill="none" stroke="{C["ink"]}" stroke-width="6"/>'''


# ── B. Whistle — "beyond the whistle": the referee's whistle, its pea is the ball
def whistle():
    cx, cy, r = 232, 214, 84
    top, mb = cy - r, cy - r + 46                  # mouthpiece runs along the body's top tangent
    lx = cx - math.sqrt(r * r - (mb - cy) ** 2)
    body = f"M62 {top} L{cx} {top} A{r} {r} 0 1 1 {lx:.1f} {mb} L62 {mb} Z"
    waves = "".join(
        f'<path d="{"M%.1f %.1f A%d %d 0 0 1 %.1f %.1f" % (*pt((cx, cy), rr, -60), rr, rr, *pt((cx, cy), rr, 10))}" '
        f'fill="none" stroke="{C["cream"]}" stroke-width="8" stroke-linecap="round"/>' for rr in (r + 26, r + 50))
    return f'''<rect width="400" height="400" rx="44" fill="{C["green"]}"/>
<g transform="rotate(-10 200 200)">
<path d="{body}" fill="{C["cream"]}" stroke="{C["cream"]}" stroke-width="10" stroke-linejoin="round"/>
<rect x="{cx - 52}" y="{top - 5}" width="34" height="18" rx="3" fill="{C["green"]}"/>
<circle cx="{cx + 4}" cy="{cy + 10}" r="26" fill="{C["red"]}"/>
{waves}</g>'''


# ── C. Keyhole — the centre circle and halfway line form a keyhole: a look behind the game
def keyhole():
    stripes = "".join(f'<rect x="{x}" y="0" width="40" height="400" fill="{C["green2"]}"/>' for x in range(0, 400, 80))
    cx, cy, r = 200, 168, 62
    hole = (f"M{cx - 20} {cy + 50} A{r} {r} 0 1 1 {cx + 20} {cy + 50} L{cx + 42} 330 L{cx - 42} 330 Z")
    return f'''<clipPath id="kh"><rect width="400" height="400" rx="44"/></clipPath>
<g clip-path="url(#kh)"><rect width="400" height="400" fill="{C["green"]}"/>{stripes}
<line x1="0" y1="{cy}" x2="400" y2="{cy}" stroke="{C["cream"]}" stroke-width="5"/>
<circle cx="{cx}" cy="{cy}" r="{r + 26}" fill="none" stroke="{C["cream"]}" stroke-width="5"/></g>
<path d="{hole}" fill="{C["ink"]}"/>
<circle cx="{cx}" cy="{cy}" r="11" fill="{C["red"]}"/>'''


# ── D. Tunnel — five arches walking out to the pitch; the fifth is the light ─
def tunnel():
    vp, out = (200, 214), []
    shades = ["#3A3128", "#2C251E", "#201B16", "#15120F"]
    for i in range(5):
        k = 0.66 ** i
        w, h = 300 * k, 330 * k
        bottom = vp[1] + (372 - vp[1]) * k
        x0 = 200 - w / 2; rr = w / 2
        d = (f"M{x0:.1f} {bottom:.1f} L{x0:.1f} {bottom - h + rr:.1f} A{rr:.1f} {rr:.1f} 0 0 1 {x0 + w:.1f} {bottom - h + rr:.1f} "
             f"L{x0 + w:.1f} {bottom:.1f} Z")
        out.append(f'<path d="{d}" fill="{shades[i] if i < 4 else C["cream"]}"/>')
        if i == 4:
            out.append(f'<circle cx="200" cy="{bottom - 9:.1f}" r="7" fill="{C["red"]}"/>')
    return f'<rect width="400" height="400" rx="44" fill="{C["sand"]}"/>' + "".join(out)


# ── E. Eclipse — two halves of a ball, and a fifth half rising behind them ───
def eclipse():
    return f'''<rect width="400" height="400" rx="44" fill="{C["cream"]}"/>
<circle cx="226" cy="176" r="112" fill="{C["red"]}"/>
<path d="M194 96 A112 112 0 0 0 194 320 Z" fill="{C["ink"]}"/>
<path d="M206 96 A112 112 0 0 1 206 320 Z" fill="{C["ink"]}"/>'''


SYMBOLS = [
    ("aperture", "العدسة · Aperture",
     "A camera iris with exactly five blades. The opening they leave is a pentagon, the patch on a football. Five, film and football in one shape, with no letters.", aperture),
    ("whistle", "الصافرة · The Whistle",
     "From his own line ما وراء الصافرة (beyond the whistle): a referee's whistle mid-blow, with the pea inside drawn as a red ball. Instantly readable at any size.", whistle),
    ("keyhole", "ثقب الباب · Keyhole",
     "The centre circle and halfway line, seen from above, become a keyhole: a look behind the game. The ball glows in the middle.", keyhole),
    ("tunnel", "النفق · The Tunnel",
     "Five arches leading out of the players' tunnel (like the photo in his banner). The fifth is the light at the end, with the ball waiting there.", tunnel),
    ("eclipse", "الكسوف · Eclipse",
     "A ball split into its two halves, with a red fifth half rising behind them like an eclipse. The red shows through the gap between the halves. The most minimal of the five.", eclipse),
]

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for slug, _, _, fn in SYMBOLS:
        body = fn()
        open(f"{out}/symbol-{slug}.svg", "w").write(wrap(400, 400, body))
        open(f"{out}/lockup-{slug}.svg", "w").write(lockup(body))
    print("ok")
