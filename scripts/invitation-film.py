import pathlib, json, math

fonts = pathlib.Path('fonts.css').read_text(encoding='utf-8')
B = lambda n: pathlib.Path('/tmp/b64_%s.txt' % n).read_text().strip()
IMG = {n: 'data:image/jpeg;base64,' + B(n) for n in ('ganesh-ji', 'radha-krishna', 'ganesh-green', 'rk-sky')}
IMG['rk-dancers'] = 'data:image/webp;base64,' + B('rk-dancers')

ROSE, ROSE2, INK, GOLD = '#8E1034', '#A61E45', '#6B2436', '#A8822C'

def flower(cx, cy, r, petal, core, n=8, op=1.0):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" opacity="%.2f"/>'
                   % (cx + r*math.cos(a), cy + r*math.sin(a), r*0.56, petal, op))
    out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r*0.52, core))
    return ''.join(out)

ORN = ('<svg class="orn" viewBox="0 0 120 26" fill="none">'
       '<path d="M2 13 H38" stroke="%s" stroke-width="1.5" stroke-linecap="round"/>'
       '<path d="M82 13 H118" stroke="%s" stroke-width="1.5" stroke-linecap="round"/>'
       % (GOLD, GOLD)
       + flower(60, 13, 8, '#E09A3C', '#B35A1E')
       + flower(47, 13, 4.5, '#D8647F', ROSE) + flower(73, 13, 4.5, '#D8647F', ROSE) + '</svg>')

SPRAY = ('<svg class="spray" viewBox="0 0 120 120" fill="none">'
         '<path d="M5 118 C5 72 23 36 62 15 C84 4 104 4 117 7" stroke="%s" stroke-width="1.7" stroke-linecap="round"/>' % GOLD
         + '<path d="M27 73 C18 63 21 50 34 48 C38 61 35 69 27 73Z" fill="#8FAE६E" opacity=".9"/>'.replace('६', '6')
         + '<path d="M49 42 C43 30 50 19 62 20 C61 33 57 41 49 42Z" fill="#8FAE6E" opacity=".9"/>'
         + flower(16, 96, 9.5, '#E09A3C', '#B35A1E') + flower(40, 56, 7.5, '#D8647F', ROSE)
         + flower(70, 22, 8.5, '#E09A3C', '#B35A1E') + '</svg>')

import math

W, H   = 1080, 1010
HORIZ  = 430          # where water meets sky
BANK   = 744          # the near bank the couple stand on
SUNX   = 706

_s = [987654321]
def _r():
    _s[0] = (1103515245 * _s[0] + 12345) % 2147483648
    return _s[0] / 2147483648.0


def _ridge(y0, amp, step, fill, op):
    """A soft hill ridge drawn right across the frame."""
    pts, x = [], -40.0
    while x < W + 60:
        pts.append((x, y0 + amp * math.sin(x / step + y0) + amp * 0.6 * _r()))
        x += 120 + 60 * _r()
    d = f'M-40 {HORIZ} L-40 {pts[0][1]:.0f} '
    for i in range(1, len(pts)):
        x0, py0 = pts[i - 1]; x1, py1 = pts[i]
        d += f'C{(x0+x1)/2:.0f} {py0:.0f} {(x0+x1)/2:.0f} {py1:.0f} {x1:.0f} {py1:.0f} '
    d += f'L{W+60} {HORIZ} Z'
    return f'<path d="{d}" fill="{fill}" opacity="{op}"/>'


def river_scene():
    _s[0] = 987654321
    o = [f'<svg class="river" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" fill="none">']
    a = o.append

    a('<defs>'
      '<linearGradient id="rvSky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#9F7FBE"/><stop offset=".28" stop-color="#CE9CBD"/>'
        '<stop offset=".58" stop-color="#EFB2AA"/><stop offset=".84" stop-color="#FBD2B2"/>'
        '<stop offset="1" stop-color="#FDE8CA"/></linearGradient>'
      '<linearGradient id="rvWat" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#F7D4B8"/><stop offset=".24" stop-color="#E0ACB0"/>'
        '<stop offset=".6" stop-color="#B790AC"/><stop offset="1" stop-color="#8A6F9E"/></linearGradient>'
      '<radialGradient id="rvGlow" cx=".5" cy=".5" r=".5">'
        '<stop offset="0" stop-color="#FFF0C8" stop-opacity=".95"/>'
        '<stop offset=".45" stop-color="#FFD79A" stop-opacity=".42"/>'
        '<stop offset="1" stop-color="#FFC98A" stop-opacity="0"/></radialGradient>'
      '<linearGradient id="rvBank" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#9CAB76"/><stop offset=".42" stop-color="#7E9060"/>'
        '<stop offset="1" stop-color="#566843"/></linearGradient>'
      '<linearGradient id="rvWarm" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#FFB859" stop-opacity=".46"/>'
        '<stop offset="1" stop-color="#FF7E4E" stop-opacity=".2"/></linearGradient>'
      '<radialGradient id="rvFly" cx=".5" cy=".5" r=".5">'
        '<stop offset="0" stop-color="#FFF3B0"/><stop offset=".4" stop-color="#FFE07A" stop-opacity=".7"/>'
        '<stop offset="1" stop-color="#FFD35C" stop-opacity="0"/></radialGradient>'
      '<radialGradient id="rvFlame" cx=".5" cy=".62" r=".5">'
        '<stop offset="0" stop-color="#FFF6D2"/><stop offset=".4" stop-color="#FFC95E"/>'
        '<stop offset="1" stop-color="#F08A2E" stop-opacity="0"/></radialGradient>'
      '</defs>')

    # ── sky ──────────────────────────────────────────────────────────
    a(f'<rect width="{W}" height="{HORIZ+4}" fill="url(#rvSky)"/>')
    for _ in range(64):
        a(f'<circle class="rv-star" cx="{_r()*W:.0f}" cy="{_r()*250:.0f}" r="{0.9+_r()*1.7:.1f}" '
          f'fill="#FFF6E2" opacity="{0.25+_r()*0.5:.2f}"/>')
    a(f'<g class="rv-sun"><circle cx="{SUNX}" cy="250" r="190" fill="url(#rvGlow)"/>'
      f'<circle cx="{SUNX}" cy="250" r="46" fill="#FFF2CE" opacity=".96"/>'
      f'<circle cx="{SUNX}" cy="250" r="46" fill="none" stroke="#FFD89A" stroke-width="6" opacity=".5"/>'
      f'<circle cx="{SUNX}" cy="250" r="68" fill="none" stroke="#FFE2AC" stroke-width="2" opacity=".28"/></g>')

    for i, (cx, cy, sc, op) in enumerate(
            [(170, 120, 1.6, .38), (690, 90, 1.25, .30), (420, 206, 2.0, .28),
             (930, 262, 1.35, .24), (90, 300, 1.2, .2), (560, 330, 1.5, .18)]):
        a(f'<g class="rv-cloud" data-sp="{0.35+i*0.2:.2f}" opacity="{op}">'
          f'<g transform="translate({cx} {cy}) scale({sc})">'
          '<ellipse cx="0" cy="0" rx="76" ry="15" fill="#FFF2E0"/>'
          '<ellipse cx="-34" cy="-7" rx="38" ry="13" fill="#FFF2E0"/>'
          '<ellipse cx="30" cy="-9" rx="44" ry="15" fill="#FFF6E8"/>'
          '<ellipse cx="4" cy="6" rx="60" ry="10" fill="#F6D8CE" opacity=".7"/></g></g>')

    for i, (bx, by, bs) in enumerate([(250, 180, 1.1), (320, 156, .85), (205, 146, .7),
                                      (840, 196, .95), (900, 216, .72), (780, 230, .6)]):
        a(f'<g class="rv-bird" data-sp="{0.5+i*0.26:.2f}">'
          f'<path transform="translate({bx} {by}) scale({bs})" d="M-12 0 C-6 -8 -2 -8 0 -2 '
          'C2 -8 6 -8 12 0" stroke="#7A5570" stroke-width="2.4" fill="none" '
          'stroke-linecap="round" opacity=".55"/></g>')

    # ── hills, then the far bank with its little temple spires ───────
    a(_ridge(336, 22, 230, '#B195C2', .6))
    a(_ridge(374, 16, 180, '#9C7FB2', .72))
    a(_ridge(404, 10, 150, '#6E5A80', .8))
    for tx, th in [(132, 30), (318, 23), (520, 34), (742, 25), (928, 30), (1046, 22)]:
        a(f'<path d="M{tx-10} 410 L{tx} {410-th} L{tx+10} 410 Z" fill="#5E4A70" opacity=".85"/>'
          f'<circle cx="{tx}" cy="{410-th-3}" r="3" fill="#E8C56A" opacity=".8"/>')

    # ── the river ────────────────────────────────────────────────────
    a(f'<rect y="{HORIZ}" width="{W}" height="{BANK-HORIZ+6}" fill="url(#rvWat)"/>')
    a('<g class="rv-refl" opacity=".7">')
    y, i = HORIZ + 4, 0
    while y < BANK:
        f = (y - HORIZ) / (BANK - HORIZ)
        a(f'<ellipse class="rv-rf" data-i="{i}" cx="{SUNX}" cy="{y:.0f}" '
          f'rx="{20+78*f+14*math.sin(i*1.7):.0f}" ry="{1.8+2.8*f:.1f}" '
          f'fill="#FFE9BE" opacity="{0.55-0.3*f:.2f}"/>')
        y += 8 + 10 * f; i += 1
    a('</g>')
    y, i = HORIZ + 10, 0
    while y < BANK - 4:
        f = (y - HORIZ) / (BANK - HORIZ)
        a(f'<rect class="rv-shim" data-i="{i}" data-f="{f:.3f}" x="{_r()*W:.0f}" y="{y:.0f}" '
          f'width="{90+300*f*(0.5+_r()):.0f}" height="{1.4+2.6*f:.1f}" rx="{1+f:.1f}" '
          f'fill="#FFF3DE" opacity="{0.16+0.26*_r():.2f}"/>')
        y += 10 + 12 * f; i += 1

    for i, (lx, ly, ls) in enumerate([(150, 540, .95), (400, 600, 1.15), (900, 556, 1.0),
                                      (620, 660, 1.35), (250, 700, 1.25), (1010, 690, 1.1),
                                      (760, 612, .9)]):
        a(f'<g class="rv-lotus" data-i="{i}" transform="translate({lx} {ly})">'
          f'<g class="sw" transform="scale({ls})">'
          '<ellipse cx="0" cy="4" rx="32" ry="9" fill="#5E7E4E" opacity=".85"/>'
          '<ellipse cx="24" cy="9" rx="18" ry="6" fill="#6B8C58" opacity=".8"/>'
          '<path d="M0 -2 C-11 -4 -13 -15 -5 -18 C-2 -24 4 -24 7 -18 C15 -15 13 -4 2 -2 Z" fill="#EE93AE"/>'
          '<path d="M0 -3 C-6 -5 -7 -13 -2 -16 C3 -13 4 -5 0 -3 Z" fill="#FBC3D2"/>'
          '<circle cx="0" cy="-9" r="2.6" fill="#F5D777"/></g></g>')

    # ── diyas set afloat, each with a flame of its own ───────────────
    for i, (dx, dy, ds) in enumerate([(330, 572, 1.0), (560, 636, 1.2), (830, 594, 1.05),
                                      (140, 648, 1.15), (690, 704, 1.3), (970, 640, 1.0)]):
        a(f'<g class="rv-diya" data-i="{i}" transform="translate({dx} {dy})">'
          f'<g class="sw" transform="scale({ds})">'
          '<ellipse cx="0" cy="7" rx="21" ry="5" fill="#FFE4C0" opacity=".4"/>'
          '<path d="M-15 0 C-13 8 -7 12 0 12 C7 12 13 8 15 0 Z" fill="#B5682E"/>'
          '<path d="M-15 0 C-8 -3 8 -3 15 0 C8 3 -8 3 -15 0 Z" fill="#D88A46"/>'
          '<g class="flame"><ellipse cx="0" cy="-9" rx="11" ry="15" fill="url(#rvFlame)"/>'
          '<path d="M0 -20 C5 -14 5 -6 0 -3 C-5 -6 -5 -14 0 -20 Z" fill="#FFD36A"/>'
          '<path d="M0 -15 C2.6 -11 2.6 -6 0 -4 C-2.6 -6 -2.6 -11 0 -15 Z" fill="#FFF6D2"/></g>'
          '</g></g>')

    for i in range(20):
        rx, ry = 790 + _r() * 300, BANK - 12 - _r() * 96
        hh = 86 + _r() * 90
        a(f'<g class="rv-reed" data-i="{i}" transform="translate({rx:.0f} {ry:.0f})"><g class="sw">'
          f'<path d="M0 0 C{-5+_r()*10:.1f} {-hh*0.5:.0f} {-7+_r()*14:.1f} {-hh*0.8:.0f} '
          f'{-10+_r()*20:.1f} {-hh:.0f}" stroke="#5E7A48" stroke-width="3" fill="none" '
          'stroke-linecap="round" opacity=".8"/></g></g>')

    # ── the near bank ────────────────────────────────────────────────
    a(f'<path d="M0 {BANK+20} C200 {BANK-10} 420 {BANK+6} 620 {BANK-8} '
      f'C820 {BANK-22} 960 {BANK+4} {W} {BANK-10} L{W} {H} L0 {H} Z" fill="url(#rvBank)"/>')
    a(f'<path d="M0 {BANK+20} C200 {BANK-10} 420 {BANK+6} 620 {BANK-8} '
      f'C820 {BANK-22} 960 {BANK+4} {W} {BANK-10}" stroke="#B4C184" stroke-width="3.4" opacity=".5"/>')

    # ── the kadamba tree leaning in from the left ────────────────────
    a('<g class="rv-tree">'
      f'<path d="M-18 {H+10} C10 880 34 740 42 600 C48 500 42 410 22 338 L68 326 '
      f'C86 404 94 500 88 604 C80 746 56 884 38 {H+10} Z" fill="#6B4A2E"/>'
      '<path d="M-6 760 C16 738 40 728 64 732" stroke="#5C3F26" stroke-width="9" '
      'fill="none" stroke-linecap="round" opacity=".9"/>'
      '<path d="M40 524 C96 496 150 474 214 470 M44 414 C110 392 164 378 224 380" '
      'stroke="#6B4A2E" stroke-width="9" fill="none" stroke-linecap="round"/>')
    for cx, cy, rr in [(44, 252, 104), (164, 306, 80), (240, 380, 62), (130, 390, 58),
                       (6, 336, 74), (224, 300, 54), (92, 176, 70)]:
        a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rr}" ry="{rr*0.76:.0f}" fill="#44633A" opacity=".95"/>')
    for cx, cy, rr in [(58, 230, 66), (172, 292, 48), (232, 368, 38), (18, 310, 46), (108, 164, 44)]:
        a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rr}" ry="{rr*0.72:.0f}" fill="#567A44" opacity=".85"/>')
    for _ in range(40):
        a(f'<circle cx="{_r()*290-24:.0f}" cy="{120+_r()*300:.0f}" r="{4+_r()*4:.1f}" '
          'fill="#F2C14E" opacity=".9"/>')
    for i in range(10):
        vx, vy, vl = 10 + _r() * 230, 330 + _r() * 110, 50 + _r() * 60
        a(f'<g class="rv-vine" data-i="{i}" transform="translate({vx:.0f} {vy:.0f})"><g class="sw">'
          f'<path d="M0 0 C6 {vl*0.4:.0f} -4 {vl*0.72:.0f} 1 {vl:.0f}" stroke="#44633A" '
          'stroke-width="2.6" fill="none" stroke-linecap="round" opacity=".85"/>'
          f'<ellipse cx="1" cy="{vl+8:.0f}" rx="7" ry="11" fill="#4E6E3E" opacity=".9"/>'
          f'<circle cx="1" cy="{vl+22:.0f}" r="4.6" fill="#F2C14E" opacity=".85"/></g></g>')
    a('</g>')

    # ── Krishna's cows, come down to the water ───────────────────────
    for i, (cx, foot, cs, body, patch) in enumerate([
            (250, 906, 0.72, '#F4ECE1', '#C09060'),    # nearest, by the tree
            (822, 838, 0.56, '#EADCC4', '#8E5A2E'),    # further along the bank
            (986, 932, 0.44, '#FBF6EE', '#B8926A')]):  # a calf at her heel
        # the drawing stands on y=154 in its own space, so lift it onto the grass
        ty = foot - 154 * cs
        a(f'<g class="rv-cow" data-i="{i}" data-x="{cx}" data-y="{ty:.1f}" '
          f'transform="translate({cx} {ty:.1f})">'
          f'<g class="sw" transform="scale({cs})">{cow(i, body, patch)}</g></g>')

    for i in range(30):
        a(f'<circle class="rv-fly" data-i="{i}" cx="{40+_r()*1000:.0f}" cy="{430+_r()*520:.0f}" '
          f'r="{6+_r()*6:.1f}" fill="url(#rvFly)" opacity="0"/>')

    for i in range(40):
        gh = 30 + _r() * 54
        a(f'<g class="rv-grass" data-i="{i}" transform="translate({_r()*W:.0f} {H+8})"><g class="sw">'
          f'<path d="M0 0 C{-6+_r()*12:.1f} {-gh*0.6:.0f} {-9+_r()*18:.1f} {-gh*0.85:.0f} '
          f'{-14+_r()*28:.1f} {-gh:.0f}" stroke="#55703C" stroke-width="3.4" fill="none" '
          'stroke-linecap="round" opacity=".9"/></g></g>')
    a(f'<rect class="rv-warm" width="{W}" height="{H}" fill="url(#rvWarm)" opacity="0"/>')
    a('</svg>')
    return ''.join(o)


def cow(uid, body='#F4ECE1', patch='#C09060', horn='#EBDCBC'):
    g = lambda n: f'{n}{uid}'
    return (
      f'<g class="cow" data-i="{uid}">'
      '<defs>'
        f'<linearGradient id="{g("cb")}" x1="0" y1="0" x2=".2" y2="1">'
          f'<stop offset="0" stop-color="#FFFBF6"/><stop offset=".5" stop-color="{body}"/>'
          f'<stop offset="1" stop-color="#CBBCA8"/></linearGradient>'
      '</defs>'
      '<ellipse cx="130" cy="156" rx="92" ry="9" fill="#3E5228" opacity=".2"/>'

      # ── the off-side pair, set back and shaded ──────────────────────
      '<g opacity=".62">'
        '<g class="legBF" style="transform-origin:78px 104px">'
          f'<path d="M78 104 L72 146" stroke="{body}" stroke-width="12" stroke-linecap="round"/>'
          '<path d="M72 146 L71 152" stroke="#5B4428" stroke-width="13" stroke-linecap="round"/></g>'
        '<g class="legFF" style="transform-origin:170px 104px">'
          f'<path d="M170 104 L176 146" stroke="{body}" stroke-width="12" stroke-linecap="round"/>'
          '<path d="M176 146 L177 152" stroke="#5B4428" stroke-width="13" stroke-linecap="round"/></g>'
      '</g>'

      # ── tail, hanging behind the rump ───────────────────────────────
      '<g class="tail" style="transform-origin:54px 62px">'
        f'<path d="M54 62 C40 80 40 108 48 128" stroke="{body}" stroke-width="7" '
        'fill="none" stroke-linecap="round"/>'
        '<path d="M48 124 C40 132 42 144 50 148 C58 143 57 132 48 124 Z" fill="#6B5230"/>'
      '</g>'

      # ── barrel ──────────────────────────────────────────────────────
      f'<path d="M52 82 C50 60 66 50 96 48 L164 50 C186 54 194 70 192 90 '
      f'C190 106 170 114 130 115 C86 115 56 104 52 82 Z" fill="url(#{g("cb")})"/>'
      f'<path d="M86 66 C106 60 128 62 140 74 C124 88 96 84 86 66 Z" fill="{patch}" opacity=".9"/>'
      f'<path d="M62 92 C74 88 86 90 92 99 C82 106 68 101 62 92 Z" fill="{patch}" opacity=".55"/>'
      '<path d="M66 110 C92 118 140 118 176 108" stroke="#CBBCA8" stroke-width="2" '
      'fill="none" opacity=".7"/>'

      # ── the shoulder hump that marks the breed ──────────────────────
      f'<path d="M150 52 C156 24 186 22 192 46 C196 60 194 74 190 84 '
      f'C182 70 166 58 150 52 Z" fill="{body}" stroke="#D8CABA" stroke-width="1.4"/>'
      f'<path d="M162 44 C172 32 184 34 187 46" stroke="#D8CABA" stroke-width="1.6" fill="none"/>'

      # ── neck, dewlap, head ──────────────────────────────────────────
      '<g class="cowHead" style="transform-origin:194px 62px">'
        f'<path d="M186 54 C206 46 226 48 236 58 L240 76 C242 92 234 102 222 102 '
        f'C206 102 196 90 192 74 Z" fill="url(#{g("cb")})"/>'
        # dewlap
        f'<path d="M192 76 C202 82 206 92 204 104 C198 100 192 92 190 84 Z" '
        f'fill="{body}" stroke="#D8CABA" stroke-width="1.2"/>'
        # skull and muzzle
        f'<path d="M216 50 C236 44 254 52 258 68 C261 82 256 96 244 100 '
        f'C232 103 220 94 216 78 Z" fill="{body}" stroke="#E0D2C0" stroke-width="1"/>'
        f'<path d="M248 76 C262 76 270 84 268 93 C266 102 254 106 245 101 '
        f'C239 97 240 80 248 76 Z" fill="#DCA9A2"/>'
        '<ellipse cx="260" cy="87" rx="2.8" ry="3.6" fill="#8E5E58"/>'
        f'<path d="M247 99 C254 103 263 101 266 97" stroke="#A8746C" stroke-width="1.7" '
        'stroke-linecap="round" fill="none"/>'
        # eye
        '<ellipse cx="236" cy="68" rx="5.4" ry="6" fill="#FFF9F2"/>'
        '<circle cx="236.6" cy="68.8" r="3.6" fill="#36220F"/>'
        '<circle cx="238.2" cy="67" r="1.2" fill="#FFF"/>'
        '<path d="M229 60 C233 56 240 56 244 60" stroke="#6B4A2E" stroke-width="1.8" '
        'stroke-linecap="round" fill="none"/>'
        # lyre horns
        f'<path d="M224 46 C214 30 218 16 229 14 C226 26 227 38 234 48 Z" fill="{horn}" '
        'stroke="#B89A66" stroke-width="1.2"/>'
        f'<path d="M244 44 C252 28 249 15 238 13 C242 25 243 36 238 46 Z" fill="{horn}" '
        'stroke="#B89A66" stroke-width="1.2"/>'
        # ear, flicking back from behind the horn
        '<g class="ear" style="transform-origin:222px 58px">'
          f'<path d="M222 58 C206 50 194 56 196 66 C200 76 216 72 224 62 Z" '
          f'fill="{patch}" stroke="#A8865A" stroke-width="1.1"/>'
          f'<path d="M219 60 C210 57 203 59 200 64" stroke="#8E6B42" stroke-width="1" fill="none"/>'
        '</g>'
        # collar and bell, worn on the neck
        '<path d="M200 60 C210 70 214 82 212 94" stroke="#A61E45" stroke-width="7" '
        'fill="none" stroke-linecap="round"/>'
        '<g class="bell" style="transform-origin:211px 92px">'
          '<path d="M206 94 C200 100 199 112 211 114 C223 112 221 100 215 94 Z" fill="#DCAE3E" '
          'stroke="#A8822C" stroke-width="1.3"/>'
          '<path d="M203 112 C208 115 215 115 219 112" stroke="#A8822C" stroke-width="1.6" fill="none"/>'
          '<circle cx="211" cy="118" r="2.8" fill="#A8822C"/>'
        '</g>'
      '</g>'

      # ── the near pair ───────────────────────────────────────────────
      '<g class="legBN" style="transform-origin:90px 106px">'
        f'<path d="M90 106 L84 148" stroke="{body}" stroke-width="13" stroke-linecap="round"/>'
        '<path d="M84 148 L83 154" stroke="#4A3620" stroke-width="14" stroke-linecap="round"/></g>'
      '<g class="legFN" style="transform-origin:160px 108px">'
        f'<path d="M160 108 L166 148" stroke="{body}" stroke-width="13" stroke-linecap="round"/>'
        '<path d="M166 148 L167 154" stroke="#4A3620" stroke-width="14" stroke-linecap="round"/></g>'
      '</g>')


def nagada(side='L'):
    u = side
    g = lambda n: n + u                      # gradient ids must be unique per instance
    return (
      '<svg class="nag" viewBox="0 0 240 278" fill="none">'
      '<defs>'
        f'<linearGradient id="{g("skin")}" x1="0" y1="0" x2="1" y2=".3">'
          '<stop offset="0" stop-color="#EFBE8C"/><stop offset=".55" stop-color="#DCA06B"/>'
          '<stop offset="1" stop-color="#B07344"/></linearGradient>'
        f'<linearGradient id="{g("kur")}" x1="0" y1="0" x2="1" y2=".2">'
          '<stop offset="0" stop-color="#FFFCF8"/><stop offset=".45" stop-color="#F5E7D9"/>'
          '<stop offset="1" stop-color="#D3B9A2"/></linearGradient>'
        f'<linearGradient id="{g("tur")}" x1="0" y1="0" x2=".9" y2=".7">'
          '<stop offset="0" stop-color="#C62C55"/><stop offset=".5" stop-color="#A61E45"/>'
          '<stop offset="1" stop-color="#6B0B29"/></linearGradient>'
        f'<linearGradient id="{g("shell")}" x1="0" y1="0" x2="1" y2="0">'
          '<stop offset="0" stop-color="#5E3410"/><stop offset=".16" stop-color="#9A6322"/>'
          '<stop offset=".38" stop-color="#C98C38"/><stop offset=".58" stop-color="#A26A22"/>'
          '<stop offset=".82" stop-color="#6E4014"/><stop offset="1" stop-color="#4A2608"/>'
        '</linearGradient>'
        f'<radialGradient id="{g("head")}" cx=".38" cy=".32" r=".8">'
          '<stop offset="0" stop-color="#FDF7E9"/><stop offset=".58" stop-color="#EBD9B6"/>'
          '<stop offset="1" stop-color="#C4A670"/></radialGradient>'
      '</defs>'

      '<ellipse cx="120" cy="264" rx="110" ry="13" fill="#8E1034" opacity=".15"/>'

      # ── crossed legs in a dhoti, spreading under the drums ──────────
      f'<path d="M26 258 C14 240 24 218 48 216 C66 215 78 226 80 240 L78 258 Z" fill="url(#{g("kur")})"/>'
      '<path d="M34 250 C44 240 60 236 74 240" stroke="#C9AE97" stroke-width="1.6" opacity=".7"/>'
      f'<path d="M216 258 C228 242 220 220 198 218 C180 217 168 228 166 242 L168 258 Z" fill="url(#{g("kur")})"/>'
      '<path d="M208 250 C198 241 184 238 170 242" stroke="#C9AE97" stroke-width="1.6" opacity=".7"/>'

      # ── torso ───────────────────────────────────────────────────────
      '<g class="body">'
        '<path d="M80 222 C72 188 72 136 92 116 L148 116 C168 136 168 188 160 222 Z" '
          f'fill="url(#{g("kur")})"/>'
        f'<path d="M92 116 C76 122 68 138 68 160 L88 164 Z" fill="url(#{g("kur")})"/>'
        f'<path d="M148 116 C164 122 172 138 172 160 L152 164 Z" fill="url(#{g("kur")})"/>'
        '<path d="M100 128 C96 160 96 194 99 218 M140 128 C144 160 144 194 141 218" '
          'stroke="#C9AE97" stroke-width="1.5" opacity=".6"/>'
        # sash across the chest
        f'<path d="M96 118 C112 146 130 176 152 214 L138 221 C118 184 102 154 86 126 Z" fill="url(#{g("tur")})"/>'
        '<path d="M96 118 C112 146 130 176 152 214" stroke="#E6C56A" stroke-width="1.8" opacity=".85"/>'
        # neck
        f'<path d="M143 62 C158 70 162 88 156 108 C152 96 148 84 140 74 Z" fill="#8E1034" opacity=".9"/>'
        '<path d="M146 70 C156 80 158 94 155 104" stroke="#6B0B29" stroke-width="1.4" opacity=".6"/>'
        f'<path d="M110 100 L130 100 L132 120 L108 120 Z" fill="url(#{g("skin")})"/>'
        '<path d="M108 114 C114 123 126 123 132 114" stroke="#B9814F" stroke-width="1.5" opacity=".55"/>'

        # ── head ──────────────────────────────────────────────────────
        '<g class="head">'
          '<path d="M100 72 C100 54 108 44 120 44 C132 44 140 54 140 72 '
              f'C140 90 132 104 120 104 C108 104 100 90 100 72 Z" fill="url(#{g("skin")})"/>'
          f'<path d="M100 72 C95 70 94 80 100 84" fill="url(#{g("skin")})" stroke="#B9814F" stroke-width="1.1"/>'
          f'<path d="M140 72 C145 70 146 80 140 84" fill="url(#{g("skin")})" stroke="#B9814F" stroke-width="1.1"/>'
          # brows
          '<path d="M106 68 C110 65 115 65 118 67 M122 67 C125 65 130 65 134 68" '
            'stroke="#3B1A20" stroke-width="2.1" stroke-linecap="round"/>'
          # eyes: small, with a lid line above
          '<ellipse cx="112" cy="75" rx="3.4" ry="2.2" fill="#FBF3EA"/>'
          '<ellipse cx="128" cy="75" rx="3.4" ry="2.2" fill="#FBF3EA"/>'
          '<circle cx="112.4" cy="76.1" r="1.7" fill="#30151A"/>'
          '<circle cx="127.6" cy="76.1" r="1.7" fill="#30151A"/>'
          '<path d="M108.4 73.6 C110 72 115 72 115.6 73.8 M124.4 73.8 C125 72 130 72 131.6 73.6" '
            'stroke="#6B4030" stroke-width="1.3" stroke-linecap="round"/>'
          # nose
          '<path d="M120 74 C122.5 80 123 85 120 87.5" stroke="#B9814F" stroke-width="1.6" '
            'stroke-linecap="round"/>'
          # moustache + open, singing mouth
          '<path d="M109 91 C114 87 126 87 131 91 C126 94.5 114 94.5 109 91 Z" fill="#30151A"/>'
          '<path d="M114 96.5 C117 99.5 123 99.5 126 96.5 C123 98.8 117 98.8 114 96.5 Z" fill="#7E2F38"/>'

          # ── pagdi: dome, pleats, brow band, side fan, tail ──────────
          f'<path d="M96 70 C92 42 106 30 120 30 C134 30 148 42 144 70 '
              'C136 58 128 53 120 53 C112 53 104 58 96 70 Z" '
              f'fill="url(#{g("tur")})"/>'
          '<path d="M100 64 C106 50 113 45 120 45 M110 58 C114 49 118 46.5 121 46 '
            'M130 58 C126 49 122 46.5 119 46 M140 64 C134 50 127 45 120 45" '
            'stroke="#7A1030" stroke-width="1.4" opacity=".7"/>'
          '<path d="M96 70 C104 59 112 54 120 54 C128 54 136 59 144 70" '
            'stroke="#E6C56A" stroke-width="2.8"/>'
          # fan of pleats rising at the side
          '<path d="M137 46 C145 34 152 28 157 29 C154 36 150 44 147 52 Z" fill="#E6C56A"/>'
          '<path d="M138 48 C147 38 153 32 157 29 M139 50 C146 42 151 36 155 32" stroke="#C09A34" stroke-width="1.1" opacity=".8"/>'
          '<path d="M137 46 C144 40 150 36 155 34" stroke="#A61E45" stroke-width="2" opacity=".5"/>'
          # tail falling behind the shoulder
          '<circle cx="120" cy="32" r="3.4" fill="#E6C56A"/>'
        '</g>'
      '</g>'

      # ── the big kettle (dhama) ──────────────────────────────────────
      '<g class="drumL">'
        f'<path d="M22 182 C20 226 44 256 76 256 C108 256 130 226 128 182 Z" fill="url(#{g("shell")})"/>'
        '<path d="M42 194 C40 222 50 242 64 250" stroke="#FFE0A0" stroke-width="5" '
          'opacity=".26" stroke-linecap="round"/>'
        '<path d="M28 188 L38 240 M46 184 L52 248 M64 182 L66 252 M82 182 L80 252 '
          'M100 184 L96 248 M116 188 L108 240" stroke="#5E3C0E" stroke-width="1.9" opacity=".5"/>'
        '<path d="M34 236 C52 246 100 246 120 234" stroke="#4A2E08" stroke-width="2.4" opacity=".45"/>'
        f'<ellipse class="headL" cx="75" cy="182" rx="53" ry="17" fill="url(#{g("head")})" '
          'stroke="#6E5210" stroke-width="2.4"/>'
        '<ellipse cx="75" cy="184" rx="17" ry="5.6" fill="#2B2018" opacity=".8"/>'
      '</g>'

      # ── the small kettle (nagada) ───────────────────────────────────
      '<g class="drumR">'
        f'<path d="M130 194 C128 228 148 256 170 256 C192 256 210 228 208 194 Z" fill="url(#{g("shell")})"/>'
        '<path d="M144 204 C142 226 150 242 160 250" stroke="#FFE0A0" stroke-width="4" '
          'opacity=".24" stroke-linecap="round"/>'
        '<path d="M136 200 L144 242 M154 195 L156 250 M170 194 L170 252 '
          'M186 195 L182 248 M202 199 L194 240" stroke="#5E3C0E" stroke-width="1.7" opacity=".5"/>'
        '<path d="M140 238 C156 248 190 246 202 236" stroke="#4A2E08" stroke-width="2.2" opacity=".45"/>'
        f'<ellipse class="headR" cx="169" cy="194" rx="40" ry="13" fill="url(#{g("head")})" '
          'stroke="#6E5210" stroke-width="2.2"/>'
        '<ellipse cx="169" cy="196" rx="12" ry="4.2" fill="#2B2018" opacity=".78"/>'
      '</g>'

      # ── arms: upper arm pivots at the shoulder, forearm at the elbow ─
      '<g class="armL">'
        f'<path d="M86 136 L52 170" stroke="url(#{g("skin")})" stroke-width="14" stroke-linecap="round"/>'
        '<g class="foreL">'
          f'<path d="M52 170 L76 164" stroke="url(#{g("skin")})" stroke-width="11.5" stroke-linecap="round"/>'
          # fist with a thumb over the stick
          f'<ellipse cx="79" cy="163" rx="8" ry="6.8" fill="url(#{g("skin")})" transform="rotate(-14 79 163)"/>'
          '<path d="M74 158 C79 155 85 157 86 162" stroke="#B9814F" stroke-width="2.6" '
            'stroke-linecap="round" fill="none"/>'
          '<path d="M86 161 L66 180" stroke="#7E4E1C" stroke-width="4.8" stroke-linecap="round"/>'
          '<circle cx="66" cy="180" r="3.6" fill="#5E3810"/>'
        '</g>'
      '</g>'
      '<g class="armR">'
        f'<path d="M154 136 L190 172" stroke="url(#{g("skin")})" stroke-width="14" stroke-linecap="round"/>'
        '<g class="foreR">'
          f'<path d="M190 172 L166 166" stroke="url(#{g("skin")})" stroke-width="11.5" stroke-linecap="round"/>'
          f'<ellipse cx="163" cy="165" rx="7.6" ry="6.4" fill="url(#{g("skin")})" transform="rotate(14 163 165)"/>'
          '<path d="M168 160 C163 157 157 159 156 164" stroke="#B9814F" stroke-width="2.4" '
            'stroke-linecap="round" fill="none"/>'
          '<path d="M156 163 L172 191" stroke="#7E4E1C" stroke-width="4.6" stroke-linecap="round"/>'
          '<circle cx="172" cy="191" r="3.4" fill="#5E3810"/>'
        '</g>'
      '</g>'
      '</svg>')
# ── the cover, and the pages that are read on the right ──
COVER = ('<div class="cov">' + SPRAY.replace('class="spray"', 'class="spray cov-tl"')
         + '<p class="deva cov-shubh">॥ शुभ विवाह ॥</p>' + ORN
         + '<p class="cov-names">Smatav <i>&amp;</i> Priyanka</p>'
         + '<p class="cov-date">29 November &middot; 4 December 2026</p></div>')

PAGES = [
    '<p class="deva inv">॥ श्री गणेशाय नमः ॥</p>'
    '<p class="deva shloka">वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ ।<br>निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा ॥</p>'
    '<p class="trans">O Lord of the curved trunk, radiant as a million suns —<br>keep all our undertakings free of obstacles, always.</p>'
    + ORN + '<p class="deva shubh">॥ शुभ विवाह ॥</p>',

    '<p class="label">With the blessings of our elders</p><p class="deva sub">बड़ों के आशीर्वाद से</p>'
    + ORN +
    '<div class="fams">'
    '<div class="fam"><h3>Bride&rsquo;s Family</h3><p class="deva fsub">वधू पक्ष</p>'
    '<p class="kin"><i>Daughter of</i>Sh. Rajender Dev Sharma<br>&amp; Smt. Vijay Laxmi Sharma</p>'
    '<p class="kin"><i>Sister of</i>Miss Arushi Sharma</p></div>'
    '<div class="fdiv"></div>'
    '<div class="fam"><h3>Groom&rsquo;s Family</h3><p class="deva fsub">वर पक्ष</p>'
    '<p class="kin"><i>Taya ji</i>Sh. Shanti Swaroop Sharma</p>'
    '<p class="kin"><i>Tayi ji</i>Smt. Raksha Sharma</p>'
    '<p class="kin"><i>Father</i>Sh. Suman Sharma</p>'
    '<p class="kin"><i>Mother</i>Smt. Malini Sharma</p>'
    '<p class="bless">with the blessings of Nana ji<br><b>O. P. Kaushal</b></p></div></div>',

    '<p class="invite">request the pleasure of your company<br>at the wedding of</p>'
    '<p class="name">Smatav</p><p class="deva sub">चि. स्मतव</p>'
    '<p class="weds">weds <span class="deva">एवं</span></p>'
    '<p class="name">Priyanka</p><p class="deva sub">सुश्री प्रियंका</p>'
    '<p class="deva hi-note">इस मंगल अवसर पर आप सपरिवार पधारकर<br>वर-वधू को आशीर्वाद प्रदान करें।</p>',

    '<p class="label">The Celebrations</p><p class="deva sub">समारोह</p>' + ORN +
    '<div class="ev"><div class="evd"><b>29</b><span>November 2026</span><i class="deva">रविवार</i></div>'
    '<div class="evb"><h3>Ladies Sangeet <span class="deva">महिला संगीत</span></h3>'
    '<ul class="prog">'
    '<li><b>12:15 PM</b> Welcome of Mama ji <span class="deva">मामा जी का स्वागत</span></li>'
    '<li><b>4:00 PM</b> Ladies Sangeet <span class="deva">महिला संगीत</span></li>'
    '<li><b>8:00 PM</b> Dinner <span class="deva">रात्रि भोज</span></li>'
    '</ul></div></div>'
    '<div class="ev"><div class="evd"><b>04</b><span>December 2026</span><i class="deva">शुक्रवार</i></div>'
    '<div class="evb"><h3>The Dham <span class="deva">धाम</span></h3>'
    '<p class="evx">The traditional Pahari feast, served to all.</p>'
    '<p class="evt">Friday &middot; 12:00 noon &ndash; 4:00 PM</p></div></div>',

    '<p class="label">Both occasions at</p><p class="deva sub">दोनों कार्यक्रम स्थल</p>'
    '<p class="venue">Lions Club Dharamshala</p><p class="deva sub">लायंस क्लब धर्मशाला</p>'
    '<p class="addr">Civil Bazar, Sharmnagar Road<br>Dharamshala, District Kangra<br>'
    'Himachal Pradesh &mdash; 176215</p>'
 + ORN +
    '<p class="deva blessing">आपकी उपस्थिति ही<br>हमारा आशीर्वाद है</p>'
    '<p class="trans">Your presence is our blessing.</p>'
    '<p class="deva sub">शुभाकांक्षी — दोनों परिवार</p>',
]

SCENE_B = 5.2
COVER_T, COVER_HOLD, OPEN_DUR = 5.2, 1.0, 1.7
HOLD, TURN = 5.0, 1.5
START = COVER_T + COVER_HOLD + OPEN_DUR
TIMES = [COVER_T] + [START + i * (HOLD + TURN) for i in range(len(PAGES))]
DURATION = TIMES[-1] + HOLD + 2.0
print('pages %d | first %.1f | last %.1f | duration %.1f' % (len(PAGES), TIMES[1], TIMES[-1], DURATION))

TPL = r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Invitation film</title><style>
@@FONTS@@
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#F7DED6}
body{font-family:'Cormorant Garamond',Georgia,serif;color:@@ROSE@@;
  background:
    radial-gradient(ellipse at 12% 6%,rgba(224,154,60,.28) 0%,transparent 42%),
    radial-gradient(ellipse at 88% 8%,rgba(216,100,127,.26) 0%,transparent 40%),
    radial-gradient(ellipse at 50% 104%,rgba(216,100,127,.22) 0%,transparent 52%),
    linear-gradient(168deg,#FDF4EE 0%,#F5DAD1 100%);}
.deva{font-family:'Tiro Devanagari Hindi',serif}

#nagL,#nagR{position:absolute;bottom:0;width:214px;z-index:8}
#nagL{left:8px} #nagR{right:8px}
.nag{width:100%;height:auto;display:block}
#shower{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:40}
.fl{position:absolute;top:0;left:0;will-change:transform,opacity}
.petal{border-radius:60% 60% 50% 50% / 70% 70% 40% 40%}

#intro{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;z-index:20}
#intro .pframe{width:620px}
#intro .inv2{font-size:74px;letter-spacing:.05em;color:@@ROSE@@}
.pframe{position:relative;padding:9px;margin:0 auto;
  background:linear-gradient(168deg,#FBEDC9 0%,#D8B771 52%,#8E6B13 100%);
  border-radius:999px 999px 16px 16px;
  box-shadow:0 18px 40px -16px rgba(142,16,52,.42),0 0 0 1px rgba(142,107,19,.5)}
.pframe::after{content:"";position:absolute;inset:5px;border:1.5px solid rgba(255,255,255,.65);
  border-radius:999px 999px 13px 13px}
.pframe img{display:block;width:100%;height:auto;border-radius:999px 999px 9px 9px}

#stage{position:absolute;inset:0;perspective:3200px;z-index:25}

/* the picture fills the top of the frame, edge to edge */
#art{position:absolute;top:0;left:0;width:1080px;height:1010px;overflow:hidden;z-index:2}
#art .river{position:absolute;inset:0;width:100%;height:100%;display:block}
.rk-fg{position:absolute;display:block;z-index:6;transform-origin:50% 82%;
  will-change:transform,left,top,width}
#artVg{position:absolute;inset:0;z-index:7;pointer-events:none;
  background:radial-gradient(ellipse at 50% 40%,transparent 58%,rgba(60,10,28,.3) 100%)}
#artHem{position:absolute;left:0;right:0;bottom:0;height:5px;z-index:10;
  background:linear-gradient(90deg,transparent,#A8822C 18%,#E6C56A 50%,#A8822C 82%,transparent)}

/* the page that is read sits under it, and turns on its left edge */
#pagewrap{position:absolute;top:1010px;left:0;width:1080px;height:910px;
  transform-style:preserve-3d;z-index:3;background:#F7DED6}
.pg{position:absolute;inset:0;overflow:hidden;
  background:linear-gradient(162deg,#FFFCFA 0%,#FDF3EF 100%)}
#leaf{position:absolute;inset:0;transform-origin:left center;transform-style:preserve-3d;z-index:6}
#leaf .face{position:absolute;inset:0;backface-visibility:hidden;overflow:hidden;
  background:linear-gradient(162deg,#FFFCFA 0%,#FDF3EF 100%)}
#lb{transform:rotateY(180deg)}
.sh{position:absolute;inset:0;opacity:0;pointer-events:none}
#shF{background:linear-gradient(90deg,rgba(74,12,34,.72) 0%,rgba(74,12,34,.26) 38%,rgba(74,12,34,0) 72%)}
#shB{background:linear-gradient(270deg,rgba(74,12,34,.68) 0%,rgba(74,12,34,.2) 42%,rgba(74,12,34,0) 76%)}
#uShade{position:absolute;inset:0;opacity:0;pointer-events:none;z-index:5;
  background:linear-gradient(90deg,rgba(74,12,34,.5) 0%,rgba(74,12,34,.14) 34%,rgba(74,12,34,0) 64%)}
#edge{position:absolute;top:0;bottom:0;left:0;width:4px;z-index:8;opacity:0;
  background:linear-gradient(90deg,rgba(255,250,236,.95),rgba(255,250,236,0))}

/* the cover, which swings open on its spine to begin */
#cover{position:absolute;inset:0;z-index:12;transform-origin:left center;
  backface-visibility:hidden;overflow:hidden;
  background:linear-gradient(162deg,#FFFCFA 0%,#FBE7DE 100%);
  box-shadow:0 40px 90px -40px rgba(142,16,52,.5)}

.inner{position:absolute;inset:34px 44px;border:1.5px solid rgba(168,130,44,.6);border-radius:8px;
  display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;text-align:center;padding:34px 38px}
.inner::before{content:"";position:absolute;inset:8px;border:1px solid rgba(168,130,44,.3);border-radius:5px}

.orn{width:250px;height:52px;margin:0}
.inner>*{margin-top:0}
.spray{width:150px;height:150px}
.cov{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%}
.cov-tl{position:absolute;top:44px;left:44px}
.cov-shubh{font-size:90px;letter-spacing:.1em;color:@@ROSE@@}
.cov-names{font-family:'Great Vibes',cursive;font-size:137px;line-height:1.15;color:@@ROSE@@;margin-top:11px}
.cov-names i{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.48em;color:@@ROSE2@@}
.cov-date{font-size:40px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:@@ROSE2@@;margin-top:26px}

.inv{font-size:79px;letter-spacing:.05em;color:@@ROSE2@@}
.shloka{font-size:55px;line-height:1.95;color:@@ROSE@@}
.trans{font-size:40px;font-style:italic;line-height:1.55;color:@@INK@@}
.shubh{font-size:92px;letter-spacing:.1em;color:@@ROSE@@}
.label{font-size:32px;letter-spacing:.2em;text-transform:uppercase;font-weight:700;color:@@ROSE2@@}
.sub{font-size:45px;color:@@INK@@}
.fams{display:flex;gap:18px;align-items:flex-start;width:100%;margin-top:11px}
.fam{flex:1}
.fam h3{font-size:28px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:@@ROSE2@@}
.fsub{font-size:36px;color:@@INK@@;margin-top:4px}
.kin{font-size:30px;line-height:1.5;color:@@ROSE@@;margin-top:12px}
.kin i{font-style:italic;font-size:.72em;letter-spacing:.06em;color:@@ROSE2@@;opacity:.92;margin-right:.45em}
.prog{list-style:none;margin-top:12px;display:grid;gap:9px;text-align:left}
.prog li{font-size:28px;line-height:1.35;color:@@INK@@}
.prog b{font-weight:600;color:@@ROSE@@;letter-spacing:.03em;margin-right:.5em}
.prog .deva{color:@@ROSE2@@;font-size:.94em;margin-left:.35em}
.bless{font-size:32px;font-style:italic;color:@@INK@@;margin-top:21px;line-height:1.5}
.bless b{font-style:normal;color:@@ROSE@@;font-size:1.12em}
.fdiv{width:1px;align-self:stretch;background:linear-gradient(180deg,transparent,rgba(168,130,44,.65),transparent)}
.invite{font-size:44px;font-style:italic;line-height:1.65;color:@@INK@@}
.name{font-family:'Great Vibes',cursive;font-size:162px;line-height:1.02;color:@@ROSE@@}
.weds{font-size:53px;font-style:italic;letter-spacing:.14em;color:@@ROSE2@@}
.weds .deva{font-style:normal;font-size:.76em}
.hi-note{font-size:37px;line-height:1.8;color:@@INK@@}
.ev{display:flex;align-items:stretch;width:100%;border:1.5px solid rgba(168,130,44,.55);
  background:rgba(255,250,248,.88);text-align:left}
.evd{width:246px;flex:none;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px 11px;
  background:rgba(224,154,60,.16);border-right:1.5px solid rgba(168,130,44,.5)}
.evd b{font-size:95px;line-height:1;font-weight:500;color:@@ROSE@@}
.evd span{font-size:20px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:@@ROSE2@@;margin-top:12px}
.evd i{font-size:26px;font-style:normal;color:@@INK@@;margin-top:5px}
.evb{padding:24px 29px}
.evb h3{font-size:48px;font-weight:600;color:@@ROSE@@}
.evb h3 .deva{font-weight:400;font-size:.7em;color:@@ROSE2@@;margin-left:10px}
.evx{font-size:36px;font-style:italic;color:@@INK@@;margin-top:7px}
.evt{font-size:29px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;color:@@ROSE@@;margin-top:16px}
.venue{font-size:76px;font-weight:600;color:@@ROSE@@}
.addr{font-size:36px;line-height:1.55;color:@@INK@@}
.blessing{font-size:62px;line-height:1.7;color:@@ROSE@@}
</style></head><body>

<div id="intro">
  <div class="pframe"><img src="@@GREEN@@" alt="Lord Ganesha in green and gold at the family puja"></div>
  <p class="deva inv2">॥ श्री गणेशाय नमः ॥</p>
</div>

<div id="stage">
  <div id="art">
    @@RIVER@@
    <img class="rk-fg" src="@@DANCERS@@" alt="Radha and Krishna on the bank of the Yamuna">
    <div id="nagL">@@NAGL@@</div><div id="nagR">@@NAGR@@</div>
    <div id="artVg"></div><div id="artHem"></div>
  </div>
  <div id="pagewrap">
    <div class="pg" id="pR"><div class="inner" id="iR"></div><div id="uShade"></div></div>
    <div id="leaf">
      <div class="face" id="lf"><div class="inner" id="ilf"></div><div class="sh" id="shF"></div><div id="edge"></div></div>
      <div class="face" id="lb"><div class="sh" id="shB"></div></div>
    </div>
  </div>
  <div id="cover"><div class="inner" id="icv"></div></div>
</div>

<div id="shower"></div>

<script>
const PAGEHTML = @@PAGES@@, TIMES = @@TIMES@@, DURATION = @@DUR@@;
const HOLD = @@HOLD@@, TURN = @@TURN@@, OPEN_DUR = @@OPEN@@, COVER_HOLD = @@COVER_HOLD@@;
const SCENE_B = @@SCENE_B@@, BOOK_IN = SCENE_B - 0.2, BEAT = 60/104, START = TIMES[1];
/* the cut-out is 660x800 and its lowest pixel sits at 0.819 of that height */
const CPW = 660, CPH = 800, FEET = 0.819, GROUND = 962;

const RV=[...document.querySelectorAll('.river')].map(sv=>{
  const grab=c=>[...sv.querySelectorAll(c)].map(el=>{
    const sw=el.querySelector(':scope > .sw');
    return {el,sw,i:+(el.dataset.i||0),f:+(el.dataset.f||0),sp:+(el.dataset.sp||1),
            b:el.getAttribute('transform')||'',sb:(sw&&sw.getAttribute('transform'))||''};
  });
  return {sun:sv.querySelector('.rv-sun'),warm:sv.querySelector('.rv-warm'),
    stars:[...sv.querySelectorAll('.rv-star')].map((el,i)=>({el,i,o:+el.getAttribute('opacity')})),
    refl:[...sv.querySelectorAll('.rv-rf')].map(el=>({el,i:+el.dataset.i,r:+el.getAttribute('rx')})),
    clouds:grab('.rv-cloud'),birds:grab('.rv-bird'),shim:grab('.rv-shim'),
    lotus:grab('.rv-lotus'),reeds:grab('.rv-reed'),vines:grab('.rv-vine'),
    grass:grab('.rv-grass'),flies:[...sv.querySelectorAll('.rv-fly')].map(el=>({el,i:+el.dataset.i})),
    diyas:[...sv.querySelectorAll('.rv-diya')].map(el=>({el,i:+el.dataset.i,
      b:el.getAttribute('transform')||'',flame:el.querySelector('.flame')})),
    cows:[...sv.querySelectorAll('.rv-cow')].map(el=>({el,i:+el.dataset.i,
      x:+el.dataset.x,y:+el.dataset.y,
      head:el.querySelector('.cowHead'),tail:el.querySelector('.tail'),
      ear:el.querySelector('.ear'),bell:el.querySelector('.bell'),
      legs:['.legBN','.legFN','.legBF','.legFF'].map(c=>el.querySelector(c))}))};
});
const clamp=(v,a,b)=>v<a?a:v>b?b:v, easeIO=p=>p<.5?4*p*p*p:1-Math.pow(-2*p+2,3)/2, easeOut=p=>1-Math.pow(1-p,3);

let seed=20261129; const rnd=()=>(seed=(seed*1103515245+12345)&0x7fffffff)/0x7fffffff;
const MARIGOLD='<svg viewBox="0 0 40 40">@@BLOOM@@</svg>';
const shower=document.getElementById('shower'), flakes=[];
for(let i=0;i<62;i++){
  const el=document.createElement('div'); el.className='fl';
  const near=rnd(), bloom=rnd()<0.40;
  const size=(bloom?22+rnd()*22:13+rnd()*14)*(0.72+near*0.6);
  if(bloom){el.innerHTML=MARIGOLD;el.firstChild.setAttribute('width',size);el.firstChild.setAttribute('height',size);}
  else{el.classList.add('petal');el.style.width=size+'px';el.style.height=(size*0.66)+'px';
       el.style.background=rnd()<0.5?'linear-gradient(140deg,#F4C285,#E09A3C)':'linear-gradient(140deg,#F0A9BC,#C94E72)';}
  if(near<0.3) el.style.filter='blur(1.6px)';            /* a little depth of field */
  shower.appendChild(el);
  flakes.push({el,x:rnd()*1120-20,y0:rnd()*2200,sp:(40+rnd()*54)*(0.7+near*0.7),amp:26+rnd()*78,ph:rnd()*6.283,
               spin:(rnd()<.5?-1:1)*(34+rnd()*96),flut:1.4+rnd()*2.2,op:(.5+rnd()*.42)*(0.6+near*0.5)});
}

const iR=document.getElementById('iR'),ilf=document.getElementById('ilf'),
      leaf=document.getElementById('leaf'),shF=document.getElementById('shF'),shB=document.getElementById('shB'),
      uShade=document.getElementById('uShade'),edge=document.getElementById('edge'),
      stage=document.getElementById('stage'),art=document.getElementById('art'),
      pagewrap=document.getElementById('pagewrap'),
      cover=document.getElementById('cover'),icv=document.getElementById('icv'),
      intro=document.getElementById('intro'),
      nags=[document.getElementById('nagL'),document.getElementById('nagR')],
      dancers=[...document.querySelectorAll('.rk-fg')];
let last={};
const setHTML=(n,k,h)=>{ if(last[k]!==h){n.innerHTML=h;last[k]=h;} };

function seek(t){
  for(const f of flakes){
    const y=((f.y0+t*f.sp)%2180+2180)%2180-200;
    const x=f.x+Math.sin(t*0.42+f.ph)*f.amp;
    const sx=Math.cos(t*f.flut+f.ph)*0.72+0.28;      /* flutter, as a petal turns edge-on */
    f.el.style.transform='translate('+x.toFixed(1)+'px,'+y.toFixed(1)+'px) rotate('+(t*f.spin+f.ph*60).toFixed(1)+'deg) scaleX('+sx.toFixed(3)+')';
    f.el.style.opacity=(f.op*clamp(t/0.9,0,1)*clamp((DURATION-t)/1.6,0,1)).toFixed(3);
  }

  const nagIn=easeOut(clamp((t-0.3)/1.1,0,1))*clamp((DURATION-t)/1.2,0,1);
  /* a drummer's hand rises slowly and snaps down onto the beat */
  const swing=p=>p<0.74?Math.sin(p/0.74*Math.PI/2):Math.cos((p-0.74)/0.26*Math.PI/2);
  const PIV={armL:[86,136],foreL:[52,170],armR:[154,136],foreR:[190,172]};
  for(let d=0;d<2;d++){
    const el=nags[d], mir=d?'scaleX(-1) ':'';
    el.style.opacity=nagIn.toFixed(3); el.style.visibility=nagIn<0.004?'hidden':'visible';
    const pA=((t/BEAT+d*0.25)%1+1)%1, pB=((t/BEAT+d*0.25+0.5)%1+1)%1;
    const lA=swing(pA), lB=swing(pB);
    /* shoulder swings, elbow whips a little behind it */
    const set=(k,a)=>el.querySelector('.'+k).setAttribute(
      'transform','rotate('+a.toFixed(2)+' '+PIV[k][0]+' '+PIV[k][1]+')');
    set('armL', 25*lA);  set('foreL', 30*swing(Math.min(pA+0.06,1)));
    set('armR',-24*lB);  set('foreR',-29*swing(Math.min(pB+0.06,1)));
    /* the skin flexes for a moment where the stick landed */
    const flex=p=>Math.max(0,1-p/0.11);
    el.querySelector('.headL').setAttribute('ry',(17+2.4*flex(pA)).toFixed(2));
    el.querySelector('.headR').setAttribute('ry',(13+1.9*flex(pB)).toFixed(2));
    /* he leans into the beat, and his head nods with it */
    const bob=3.2*Math.sin(2*Math.PI*t/BEAT), nod=2.4*Math.sin(2*Math.PI*t/BEAT-0.5);
    el.style.transform=mir+'translateY('+bob.toFixed(2)+'px)';
    el.querySelector('.body').setAttribute('transform',
      'rotate('+(1.5*Math.sin(2*Math.PI*t/(BEAT*2))).toFixed(2)+' 120 230)');
    el.querySelector('.head').setAttribute('transform',
      'translate(0 '+nod.toFixed(2)+') rotate('+(2.2*Math.sin(2*Math.PI*t/(BEAT*2)+0.4)).toFixed(2)+' 120 104)');
  }

  /* ── the story told on the left-hand page ──────────────────────────
     The sun sinks over the Yamuna, the water catches it, reeds and grass
     move on the breeze, and the fireflies come out as it darkens. */
  const ST=Math.max(0,t-START), dusk=clamp(ST/22,0,1);
  const A2=START+10.5, A3=START+20.5;
  const act3=clamp((t-A3)/5,0,1);
  for(const R of RV){
    R.sun.setAttribute('transform','translate(0 '+(16*dusk).toFixed(1)+')');
    R.warm.setAttribute('opacity',(0.5*act3).toFixed(3));
    for(const s of R.stars)
      s.el.setAttribute('opacity',(s.o*(0.28+0.72*dusk)*(0.76+0.24*Math.sin(t*2.1+s.i))).toFixed(3));
    for(const c of R.clouds)
      c.el.setAttribute('transform','translate('+(c.sp*ST*2.6).toFixed(1)+' 0)');
    for(const b of R.birds)
      b.el.setAttribute('transform','translate('+(-b.sp*ST*5).toFixed(1)+' '+(5*Math.sin(ST*0.7+b.i)).toFixed(1)+')');
    for(const q of R.shim)
      q.el.setAttribute('transform','translate('+(26*q.f*Math.sin(ST*(0.3+0.12*q.f)+q.i*0.9)).toFixed(1)+' 0)');
    for(const r of R.refl)
      r.el.setAttribute('rx',(r.r*(1+0.14*Math.sin(ST*1.7+r.i*0.75))).toFixed(1));
    for(const l of R.lotus){
      l.el.setAttribute('transform',l.b+' translate(0 '+(3.2*Math.sin(ST*0.75+l.i*1.3)).toFixed(2)+')');
      l.sw.setAttribute('transform',l.sb+' rotate('+(3*Math.sin(ST*0.5+l.i)).toFixed(2)+')');
    }
    for(const r of R.reeds) r.sw.setAttribute('transform','rotate('+(3.4*Math.sin(ST*0.9+r.i*0.7)).toFixed(2)+')');
    for(const v of R.vines) v.sw.setAttribute('transform','rotate('+(4.2*Math.sin(ST*0.8+v.i*1.1)).toFixed(2)+')');
    for(const g of R.grass) g.sw.setAttribute('transform','rotate('+(5*Math.sin(ST*1.15+g.i*0.6)).toFixed(2)+')');
    const flyIn=clamp((ST-9)/5,0,1);
    for(const f of R.flies){
      f.el.setAttribute('transform','translate('+(22*Math.sin(ST*0.42+f.i*1.7)).toFixed(1)+' '
        +(16*Math.sin(ST*0.33+f.i*2.3)).toFixed(1)+')');
      f.el.setAttribute('opacity',(flyIn*(0.3+0.7*Math.max(0,Math.sin(ST*1.5+f.i*1.9)))).toFixed(3));
    }
  }

  /* Krishna's cows come down the bank, then settle to graze */
  for(const R of RV){
    for(const c of R.cows){
      const wp=easeIO(clamp((ST-0.6-c.i*1.5)/8.0,0,1));
      c.el.setAttribute('transform','translate('+(c.x+(1320-c.x)*(1-wp)).toFixed(1)+' '+c.y+')');
      const walking=wp<0.999;
      const step=2*Math.PI*(ST*1.55+c.i*0.37);
      const sw=walking?20:0;
      c.legs[0].style.transform='rotate('+( sw*Math.sin(step)).toFixed(2)+'deg)';
      c.legs[1].style.transform='rotate('+(-sw*Math.sin(step)).toFixed(2)+'deg)';
      c.legs[2].style.transform='rotate('+(-sw*Math.sin(step+0.5)).toFixed(2)+'deg)';
      c.legs[3].style.transform='rotate('+( sw*Math.sin(step+0.5)).toFixed(2)+'deg)';
      /* head high while she walks, down in the grass once she stops */
      const graze=(1-wp)*0+clamp((ST-9.5-c.i*1.5)/2.2,0,1);
      const chew=1.6*Math.sin(2*Math.PI*ST*2.6+c.i);
      c.head.style.transform='rotate('+(30*graze+chew*graze+2*Math.sin(step)*(walking?1:0)).toFixed(2)+'deg)';
      c.tail.style.transform='rotate('+(7*Math.sin(2*Math.PI*ST*0.75+c.i*1.9)).toFixed(2)+'deg)';
      /* an ear flicks now and then */
      const fl=Math.max(0,Math.sin(2*Math.PI*(ST*0.33+c.i*0.4))-0.93)/0.07;
      c.ear.style.transform='rotate('+(-22*fl).toFixed(2)+'deg)';
      c.bell.style.transform='rotate('+((walking?9:3)*Math.sin(step+0.9)).toFixed(2)+'deg)';
    }
    /* lamps set afloat: each bobs on the water and its flame gutters */
    for(const d of R.diyas){
      d.el.setAttribute('transform',d.b+' translate('+(7*Math.sin(ST*0.31+d.i*1.7)).toFixed(2)
        +' '+(4.5*Math.sin(ST*0.86+d.i*2.3)).toFixed(2)+')');
      const fk=0.86+0.14*Math.sin(ST*9.1+d.i*2.1)+0.07*Math.sin(ST*23.3+d.i);
      d.flame.style.transformOrigin='0px 0px';
      d.flame.style.transform='scale('+(0.94+0.1*fk).toFixed(3)+','+fk.toFixed(3)
        +') rotate('+(3.5*Math.sin(ST*3.7+d.i)).toFixed(2)+'deg)';
      d.flame.style.opacity=(0.82+0.18*fk).toFixed(3);
    }
  }

  /* Radha and Krishna: they come along the bank and meet, stand a while by
     the water, and then dance as the sky turns gold. */
  let cw,dx,dy=0,cop=1,danceAmt;
  if(t<A2){
    const p=easeIO(clamp((t-START)/(A2-START),0,1));
    cw=330+128*p; dx=440-440*p; danceAmt=0;
    dy=-7*Math.abs(Math.sin(Math.PI*(t-START)/0.62))*(1-0.85*p);   /* the step of a walk */
    cop=clamp((t-START)/1.4,0,1);
  } else if(t<A3){
    const p=easeIO(clamp((t-A2)/(A3-A2),0,1));
    cw=458+54*p; dx=0; danceAmt=0;
    dy=-3.4*Math.sin(2*Math.PI*(t-A2)/3.1);                        /* at rest, breathing */
  } else {
    cw=512+74*easeIO(clamp((t-A3)/(DURATION-A3),0,1)); dx=0;
    danceAmt=easeIO(clamp((t-A3)/2.6,0,1));
  }
  const ph=t/BEAT;
  const bounce=-13*Math.abs(Math.sin(Math.PI*ph))*danceAmt;
  const sway=2.4*Math.sin(2*Math.PI*ph/4)*(0.3+0.7*danceAmt);
  const skew=1.2*Math.sin(2*Math.PI*ph/4+0.6)*danceAmt;
  const pulse=1+0.018*Math.abs(Math.sin(Math.PI*ph))*danceAmt;
  const chF=cw*CPH/CPW;                       /* the cut-out keeps its proportions */
  for(const d of dancers){
    d.style.width=cw.toFixed(1)+'px';
    d.style.left=(540-cw/2+dx).toFixed(1)+'px';
    d.style.top=(GROUND-FEET*chF+dy).toFixed(1)+'px';
    d.style.transform='translateY('+bounce.toFixed(2)+'px) rotate('+sway.toFixed(2)
      +'deg) skewX('+skew.toFixed(2)+'deg) scale('+pulse.toFixed(4)+')';
    d.style.opacity=cop.toFixed(3);
  }

  const iin=easeOut(clamp(t/1.0,0,1)), iout=1-easeIO(clamp((t-(SCENE_B-0.9))/0.9,0,1));
  intro.style.opacity=(iin*iout).toFixed(3);
  intro.style.transform='scale('+(0.94+0.06*iin).toFixed(4)+')';
  intro.style.visibility=(iin*iout)<0.004?'hidden':'visible';

  const bin=easeOut(clamp((t-BOOK_IN)/1.0,0,1)), tail=clamp((DURATION-t)/1.4,0,1);
  stage.style.opacity=(bin*tail).toFixed(3);
  stage.style.visibility=bin<0.004?'hidden':'visible';
  art.style.transform='scale('+(1+0.016*Math.sin(t*0.17)).toFixed(4)+')';   /* the camera breathes */

  /* the cover swings open on its spine to begin the reading */
  setHTML(icv,'C',PAGEHTML[0]);
  const cvIn=easeOut(clamp((t-TIMES[0]+0.2)/0.8,0,1));
  const cvP=clamp((t-(TIMES[0]+COVER_HOLD))/OPEN_DUR,0,1), cvE=easeIO(cvP);
  cover.style.transform='rotateY('+(-115*cvE).toFixed(2)+'deg)';
  cover.style.opacity=(cvIn*(1-0.35*cvE)*tail).toFixed(3);
  cover.style.visibility=(cvIn<0.004||cvP>=1)?'hidden':'visible';

  /* and then the pages turn, one at a time, under the picture */
  let i=1; for(let k=1;k<TIMES.length;k++) if(t>=TIMES[k]) i=k;
  const last_=PAGEHTML.length-1;
  const p=(i>=last_)?0:clamp((t-(TIMES[i]+HOLD))/TURN,0,1);
  setHTML(ilf,'F',PAGEHTML[i]); setHTML(iR,'R',PAGEHTML[Math.min(i+1,last_)]);

  const e=easeIO(p);
  leaf.style.transform='rotateY('+(-180*e).toFixed(2)+'deg)';
  leaf.style.visibility=(p>=1)?'hidden':'visible';
  const lift=Math.sin(Math.PI*p);
  shF.style.opacity=(0.80*lift).toFixed(3);
  shB.style.opacity=(0.70*clamp((1-p)*2.1,0,1)*(p>0.45?1:0)).toFixed(3);
  uShade.style.opacity=(0.55*lift).toFixed(3);
  edge.style.opacity=(0.75*lift).toFixed(3);
}
window.PAGEHTML=PAGEHTML; window.seek=seek; window.DURATION=DURATION; seek(0);
</script></body></html>'''

BLOOM = flower(20, 20, 7.6, '#E09A3C', '#B35A1E', n=9)
html = (TPL.replace('@@FONTS@@', fonts)
           .replace('@@GREEN@@', IMG['ganesh-green'])
           .replace('@@DANCERS@@', IMG['rk-dancers']).replace('@@RIVER@@', river_scene())
           .replace('@@BLOOM@@', BLOOM)
           .replace('@@NAGL@@', nagada('L')).replace('@@NAGR@@', nagada('R'))
           .replace('@@PAGES@@', json.dumps([COVER] + PAGES))
           .replace('@@TIMES@@', json.dumps([round(x, 3) for x in TIMES]))
           .replace('@@DUR@@', str(round(DURATION, 2)))
           .replace('@@HOLD@@', str(HOLD)).replace('@@TURN@@', str(TURN))
           .replace('@@OPEN@@', str(OPEN_DUR)).replace('@@COVER_HOLD@@', str(COVER_HOLD))
           .replace('@@SCENE_B@@', str(SCENE_B))
           .replace('@@ROSE2@@', ROSE2).replace('@@ROSE@@', ROSE).replace('@@INK@@', INK))
pathlib.Path('video.html').write_text(html, encoding='utf-8')
print('video.html %.0f KB  duration %.1fs' % (len(html)/1024, DURATION))
