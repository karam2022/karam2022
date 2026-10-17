"""Shape Arabic text with HarfBuzz and emit SVG path data (font-independent outlines)."""
import io, uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

N = "/tmp/claude-0/-home-user-karam2022/e9bc8526-d92f-57c8-9b17-6e4d1492be95/scratchpad/npmf/"
FONTS = {
 "ruqaa": N+"fontsource-aref-ruqaa-5.3.0/package/files/aref-ruqaa-arabic-700-normal.woff2",
 "lalezar": N+"fontsource-lalezar-5.3.0/package/files/lalezar-arabic-400-normal.woff2",
 "kufi": N+"fontsource-reem-kufi-5.3.0/package/files/reem-kufi-arabic-700-normal.woff2",
 "kufi4": N+"fontsource-reem-kufi-5.3.0/package/files/reem-kufi-arabic-400-normal.woff2",
 "rakkas": N+"fontsource-rakkas-5.3.0/package/files/rakkas-arabic-400-normal.woff2",
 "marhey": N+"fontsource-marhey-5.3.0/package/files/marhey-arabic-700-normal.woff2",
 "mont": N+"mont/package/files/montserrat-latin-800-normal.woff2",
 "mont5": N+"mont/package/files/montserrat-latin-500-normal.woff2",
}
_cache = {}
def feats(name):
    # Reem Kufi's rclt tucks the khah dot into the lam joint (reads as النامس) — use the plain forms
    return {"rclt": False} if name.startswith("kufi") else {}
def _load(name):
    if name not in _cache:
        tt = TTFont(FONTS[name]); buf = io.BytesIO(); tt.flavor = None; tt.save(buf)
        data = buf.getvalue(); tt = TTFont(io.BytesIO(data))
        _cache[name] = (tt, hb.Font(hb.Face(data)))
    return _cache[name]

def text_path(text, font, size, x=0, y=0, anchor="middle", tracking=0):
    """Return (d, bbox) for text with baseline at y. anchor: start(=right edge for RTL)/middle/end."""
    tt, hfont = _load(font)
    upem = tt["head"].unitsPerEm; s = size / upem
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hfont, buf, feats(font))
    gs = tt.getGlyphSet(); order = tt.getGlyphOrder()
    total = sum(p.x_advance for p in buf.glyph_positions) + tracking/s*(len(buf.glyph_infos)-1)
    if anchor == "middle": ox = x - total*s/2
    elif anchor == "end": ox = x - total*s
    else: ox = x
    parts = []; bp = BoundsPen(gs); cx = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        g = order[info.codepoint]
        t = (s, 0, 0, -s, ox + (cx+pos.x_offset)*s, y - pos.y_offset*s)
        pen = SVGPathPen(gs); gs[g].draw(TransformPen(pen, t)); gs[g].draw(TransformPen(bp, t))
        if pen.getCommands(): parts.append(pen.getCommands())
        cx += pos.x_advance + tracking/s
    # one subpath list per glyph: overlapping glyphs must be filled separately or nonzero winding cancels ink
    return SEP.join(parts), bp.bounds

SEP = "\x00"
def P(d, attrs=""):
    """Emit one <path> per glyph."""
    return "".join(f'<path d="{x}" {attrs}/>' for x in d.split(SEP))
