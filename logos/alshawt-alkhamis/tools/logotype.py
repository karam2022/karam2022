"""Round 6 — custom logotype: الشوط الخامس constructed stroke by stroke on a grid (modern Kufic).
Baseline at y=0 (negative is up); the word is written right to left from x=0."""
import os, sys
from five import wrap


def build(w=16, h=50, A=160, gap=32, word_gap=62, tooth=30):
    """Return (ink_paths, red_paths, dots, width). Paths are stroke centrelines."""
    ink, red, dots = [], [], []
    L = lambda *pts: ink.append("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts))
    x = 0
    # ── الشوط ──────────────────────────────────────────────
    L((x, -A), (x, 0))                                   # ا
    x -= gap
    lam = x
    shin = [lam - 30, lam - 56, lam - 82]
    waw_r, waw_l = shin[-1] - 26, shin[-1] - 26 - 46
    L((lam, -A), (lam, 0), (waw_r, 0))                   # ل + baseline through ش into و
    for tx in shin:
        L((tx, 0), (tx, -tooth))                         # ش teeth
    cx = shin[1]
    dots += [(cx - 13, -tooth - 26), (cx + 13, -tooth - 26), (cx, -tooth - 50)]   # ش dots
    L((waw_r, 0), (waw_r, -h + 6), (waw_l, -h + 6), (waw_l, 0), (waw_r, 0))      # و head
    L((waw_r, 0), (waw_r - 8, 34), (waw_r - 44, 58))     # و tail
    x = waw_l - gap
    # ط: baseline tail on the right, loop on the left, stem from the loop's top
    t_r, t_l = x, x - 92
    loop_r = t_l + 54
    L((t_r, 0), (t_l, 0), (t_l, -h + 6), (loop_r, -h + 6), (loop_r, 0))
    L((loop_r - 16, -h + 6), (loop_r - 16, -A))
    x = t_l - word_gap
    # ── الخامس ─────────────────────────────────────────────
    L((x, -A), (x, 0))                                   # ا
    x -= gap
    lam2 = x
    khah_r = lam2 - 22
    khah_top_r, khah_top_l = khah_r - 26, khah_r - 26 - 44
    alef_f = khah_top_l - 14
    L((lam2, -A), (lam2, 0), (alef_f, 0), (alef_f, -A))  # ل … ـا (baseline runs under خ)
    L((khah_r, 0), (khah_top_r, -h), (khah_top_l, -h))   # خ: diagonal + top bar
    dots.append(((khah_top_r + khah_top_l) / 2, -h - 26))
    x = alef_f - gap
    # م initial — its loop is the ٥, in red
    m_r, m_l = x, x - 46
    mc = (m_r + m_l) / 2; rr = 23
    red.append(f"M{mc:.1f} {-h - 16:.1f} Q{m_r:.1f} {-h + 4:.1f} {m_r:.1f} {-rr:.1f} "
               f"A{rr} {rr} 0 0 1 {m_l:.1f} {-rr:.1f} Q{m_l:.1f} {-h + 4:.1f} {mc:.1f} {-h - 16:.1f}Z")
    # س final: two teeth, a third rising into the bowl, bowl below the baseline
    s1, s2, s3 = m_l - 24, m_l - 48, m_l - 72
    bowl_l = s3 - 84
    L((mc, 0), (s3, 0))
    for tx in (s1, s2, s3):
        L((tx, 0), (tx, -tooth + 4))
    ink.append(f"M{s3:.1f} 0 A{(s3 - bowl_l) / 2:.1f} {(s3 - bowl_l) / 2 * 0.62:.1f} 0 0 1 {bowl_l:.1f} 0 L{bowl_l:.1f} {-tooth:.1f}")
    return ink, red, dots, -bowl_l


def logotype(w=16, ink="#161513", accent="#C4352B", bg="#F1E8D8", pad=60, dot_k=1.35, cap="butt", **kw):
    paths, reds, dots, width = build(w=w, **kw)
    A = kw.get("A", 160)
    W, H = width + 2 * pad + w, A + 2 * pad + 70
    ox, oy = width + pad + w / 2, pad + A
    st = f'fill="none" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round"'
    body = "".join(f'<path d="{d}" stroke="{ink}" {st}/>' for d in paths)
    body += "".join(f'<path d="{d}" stroke="{accent}" {st}/>' for d in reds)
    s = w * dot_k / 2
    body += "".join(f'<path d="M{x:.1f} {y - s:.1f} L{x + s:.1f} {y:.1f} L{x:.1f} {y + s:.1f} L{x - s:.1f} {y:.1f}Z" fill="{ink}"/>' for x, y in dots)
    return wrap(round(W), round(H), f'<g transform="translate({ox:.1f} {oy:.1f})">{body}</g>', bg)


if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    open(f"{out}/logotype-light.svg", "w").write(logotype(w=10))
    open(f"{out}/logotype-regular.svg", "w").write(logotype(w=16))
    open(f"{out}/logotype-bold.svg", "w").write(logotype(w=22, dot_k=1.25))
    open(f"{out}/logotype-dark.svg", "w").write(logotype(w=16, ink="#C9A45C", accent="#C4352B", bg="#0F0E0C"))
    open(f"{out}/logotype-green.svg", "w").write(logotype(w=16, ink="#F1E8D8", accent="#E2574C", bg="#2F6B4A"))
    print("ok")


def lockup_full(w=16, ink="#161513", accent="#C4352B", bg="#F1E8D8", en="#2F6B4A", mark=None):
    """Logotype + English line beneath; optional mark (SVG body in a 400 box) on the right."""
    from shape import text_path, P
    paths, reds, dots, width = build(w=w)
    A, pad = 160, 70
    mark_w = 300 if mark else 0
    W, H = width + 2 * pad + w + mark_w, A + 2 * pad + 150
    ox, oy = width + pad + w / 2, pad + A
    st = f'fill="none" stroke-width="{w}" stroke-linecap="butt" stroke-linejoin="round"'
    body = "".join(f'<path d="{d}" stroke="{ink}" {st}/>' for d in paths)
    body += "".join(f'<path d="{d}" stroke="{accent}" {st}/>' for d in reds)
    s = w * 1.35 / 2
    body += "".join(f'<path d="M{x:.1f} {y - s:.1f} L{x + s:.1f} {y:.1f} L{x:.1f} {y + s:.1f} L{x - s:.1f} {y:.1f}Z" fill="{ink}"/>' for x, y in dots)
    e, eb = text_path("THE FIFTH HALF", "mont", 30, 0, 0, "start", tracking=11)
    ex = pad + w / 2 + (width - (eb[2] - eb[0])) / 2 - eb[0]
    m = f'<g transform="translate({width + 2 * pad + 20:.1f} {(H - 260) / 2:.1f}) scale(.65)">{mark}</g>' if mark else ""
    return wrap(round(W), round(H), f'<g transform="translate({ox:.1f} {oy:.1f})">{body}</g>'
                f'<g transform="translate({ex:.1f} {oy + 128:.1f})">{P(e, f"fill=\"{en}\"")}</g>{m}', bg)


def five_avatar(bg="#F1E8D8", accent="#C4352B", w=34):
    """The meem's ٥ on its own, at avatar scale."""
    c, rr = 200, 74
    d = (f"M{c} {c - 150} Q{c + rr} {c - 80} {c + rr} {c + 30} A{rr} {rr} 0 0 1 {c - rr} {c + 30} "
         f"Q{c - rr} {c - 80} {c} {c - 150}Z")
    return wrap(400, 400, f'<rect width="400" height="400" rx="44" fill="{bg}"/>'
                f'<path d="{d}" fill="none" stroke="{accent}" stroke-width="{w}" stroke-linejoin="round" transform="translate(0 18)"/>')
