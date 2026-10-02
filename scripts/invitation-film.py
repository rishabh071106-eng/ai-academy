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

_s = [987654321]
def _r():
    _s[0] = (1103515245 * _s[0] + 12345) % 2147483648
    return _s[0] / 2147483648.0

W, H   = 660, 800
HORIZ  = 468          # where water meets sky
BANK   = 690          # the near bank the couple stand on


def river_scene():
    _s[0] = 987654321
    o = ['<svg class="river" viewBox="0 0 660 800" preserveAspectRatio="xMidYMid slice" fill="none">']
    a = o.append

    a('<defs>'
      '<linearGradient id="rvSky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#A98BC4"/><stop offset=".26" stop-color="#D3A3C0"/>'
        '<stop offset=".55" stop-color="#F0B4AC"/><stop offset=".82" stop-color="#FBD2B4"/>'
        '<stop offset="1" stop-color="#FDE7C9"/></linearGradient>'
      '<linearGradient id="rvWat" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#F6D3B8"/><stop offset=".22" stop-color="#E0AEB2"/>'
        '<stop offset=".58" stop-color="#B992AE"/><stop offset="1" stop-color="#8E73A0"/>'
      '</linearGradient>'
      '<radialGradient id="rvGlow" cx=".5" cy=".5" r=".5">'
        '<stop offset="0" stop-color="#FFF0C8" stop-opacity=".95"/>'
        '<stop offset=".45" stop-color="#FFD79A" stop-opacity=".45"/>'
        '<stop offset="1" stop-color="#FFC98A" stop-opacity="0"/></radialGradient>'
      '<linearGradient id="rvBank" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#97A672"/><stop offset=".5" stop-color="#798B5C"/>'
        '<stop offset="1" stop-color="#5A6B42"/></linearGradient>'
      '<linearGradient id="rvWarm" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#FFB859" stop-opacity=".5"/>'
        '<stop offset="1" stop-color="#FF7E4E" stop-opacity=".22"/></linearGradient>'
      '<radialGradient id="rvFly" cx=".5" cy=".5" r=".5">'
        '<stop offset="0" stop-color="#FFF3B0"/><stop offset=".4" stop-color="#FFE07A" stop-opacity=".7"/>'
        '<stop offset="1" stop-color="#FFD35C" stop-opacity="0"/></radialGradient>'
      '</defs>')

    # ── sky ──────────────────────────────────────────────────────────
    a(f'<rect width="{W}" height="{HORIZ+4}" fill="url(#rvSky)"/>')

    # early stars, high up, which fade in as dusk falls
    for _ in range(46):
        x, y = _r() * W, _r() * 230
        a(f'<circle class="rv-star" cx="{x:.0f}" cy="{y:.0f}" r="{0.8 + _r()*1.5:.1f}" '
          f'fill="#FFF6E2" opacity="{0.25 + _r()*0.5:.2f}"/>')

    # the low sun, and its halo
    a('<g class="rv-sun"><circle cx="430" cy="300" r="165" fill="url(#rvGlow)"/>'
      '<circle cx="430" cy="300" r="40" fill="#FFF2CE" opacity=".96"/>'
      '<circle cx="430" cy="300" r="40" fill="none" stroke="#FFD89A" stroke-width="6" opacity=".55"/>'
      '<circle cx="430" cy="300" r="58" fill="none" stroke="#FFE2AC" stroke-width="2" opacity=".3"/></g>')

    # drifting cloud banks
    for i, (cx, cy, sc, op) in enumerate(
            [(120, 150, 1.35, .40), (470, 108, 1.05, .32),
             (300, 232, 1.75, .30), (575, 300, 1.15, .26), (90, 320, 1.0, .22)]):
        a(f'<g class="rv-cloud" data-sp="{0.35 + i*0.22:.2f}" opacity="{op}">'
          f'<g transform="translate({cx} {cy}) scale({sc})">'
          '<ellipse cx="0" cy="0" rx="76" ry="15" fill="#FFF2E0"/>'
          '<ellipse cx="-34" cy="-7" rx="38" ry="13" fill="#FFF2E0"/>'
          '<ellipse cx="30" cy="-9" rx="44" ry="15" fill="#FFF6E8"/>'
          '<ellipse cx="4" cy="6" rx="60" ry="10" fill="#F6D8CE" opacity=".7"/>'
          '</g></g>')

    # birds returning home
    for i, (bx, by, bs) in enumerate([(150, 196, 1.0), (196, 176, .78), (122, 166, .62),
                                      (520, 214, .85), (556, 232, .66)]):
        a(f'<g class="rv-bird" data-sp="{0.5 + i*0.3:.2f}">'
          f'<path transform="translate({bx} {by}) scale({bs})" d="M-11 0 C-6 -7 -2 -7 0 -2 '
          'C2 -7 6 -7 11 0" stroke="#7A5570" stroke-width="2.2" fill="none" '
          'stroke-linecap="round" opacity=".6"/></g>')

    # ── far hills, hazy with distance ────────────────────────────────
    a(f'<path d="M0 {HORIZ} L0 372 C70 332 134 356 196 334 C262 310 318 344 384 330 '
      f'C452 314 520 346 592 330 L{W} 324 L{W} {HORIZ} Z" fill="#B195C2" opacity=".62"/>')
    a(f'<path d="M0 {HORIZ} L0 404 C84 378 150 398 226 384 C300 370 366 398 442 388 '
      f'C520 378 586 400 {W} 392 L{W} {HORIZ} Z" fill="#9C7FB2" opacity=".72"/>')

    # the far bank: a line of trees and little temple spires
    a(f'<path d="M0 {HORIZ} L0 436 C60 428 96 440 140 432 C190 422 230 438 286 430 '
      f'C340 422 392 438 448 430 C510 421 570 436 {W} 428 L{W} {HORIZ} Z" fill="#6E5A80" opacity=".8"/>')
    for tx, th in [(84, 26), (212, 20), (356, 30), (498, 22), (602, 26)]:
        a(f'<path d="M{tx-9} 438 L{tx} {438-th} L{tx+9} 438 Z" fill="#5E4A70" opacity=".85"/>'
          f'<circle cx="{tx}" cy="{438-th-3}" r="2.6" fill="#E8C56A" opacity=".8"/>')

    # ── the river ────────────────────────────────────────────────────
    a(f'<rect y="{HORIZ}" width="{W}" height="{BANK-HORIZ+6}" fill="url(#rvWat)"/>')
    # the sun laid out on the water
    a('<g class="rv-refl" opacity=".72">')
    y = HORIZ + 4
    i = 0
    while y < BANK:
        f  = (y - HORIZ) / (BANK - HORIZ)
        rx = 16 + 54 * f + 10 * math.sin(i * 1.7)
        a(f'<ellipse class="rv-rf" data-i="{i}" cx="430" cy="{y:.0f}" rx="{rx:.0f}" '
          f'ry="{1.6 + 2.4*f:.1f}" fill="#FFE9BE" opacity="{0.55 - 0.3*f:.2f}"/>')
        y += 7 + 9 * f
        i += 1
    a('</g>')
    # ripple bands across the whole river, nearer ones longer and lazier
    y, i = HORIZ + 10, 0
    while y < BANK - 4:
        f  = (y - HORIZ) / (BANK - HORIZ)
        x0 = _r() * W
        ln = 50 + 190 * f * (0.5 + _r())
        a(f'<rect class="rv-shim" data-i="{i}" data-f="{f:.3f}" x="{x0:.0f}" y="{y:.0f}" '
          f'width="{ln:.0f}" height="{1.2 + 2.2*f:.1f}" rx="{1 + f:.1f}" '
          f'fill="#FFF3DE" opacity="{0.16 + 0.26*_r():.2f}"/>')
        y += 9 + 11 * f
        i += 1

    # lotus pads and blooms afloat
    for i, (lx, ly, ls) in enumerate([(96, 560, .85), (246, 616, 1.05), (556, 578, .9),
                                      (392, 650, 1.2), (142, 664, 1.1), (610, 648, .95)]):
        a(f'<g class="rv-lotus" data-i="{i}" transform="translate({lx} {ly})"><g class="sw" transform="scale({ls})">'
          '<ellipse cx="0" cy="4" rx="30" ry="9" fill="#5E7E4E" opacity=".85"/>'
          '<path d="M-30 4 L-6 2" stroke="#4A6A3C" stroke-width="2"/>'
          '<ellipse cx="22" cy="9" rx="17" ry="5.5" fill="#6B8C58" opacity=".8"/>'
          '<path d="M0 -2 C-11 -4 -13 -15 -5 -18 C-2 -24 4 -24 7 -18 C15 -15 13 -4 2 -2 Z" fill="#EE93AE"/>'
          '<path d="M0 -3 C-6 -5 -7 -13 -2 -16 C3 -13 4 -5 0 -3 Z" fill="#FBC3D2"/>'
          '<circle cx="0" cy="-9" r="2.4" fill="#F5D777"/>'
          '</g></g>')

    # reeds standing in the shallows
    for i in range(14):
        rx = 470 + _r() * 185
        ry = BANK - 10 - _r() * 70
        hh = 70 + _r() * 70
        a(f'<g class="rv-reed" data-i="{i}" transform="translate({rx:.0f} {ry:.0f})">'
          f'<g class="sw"><path d="M0 0 C{-4+_r()*8:.1f} {-hh*0.5:.0f} {-6+_r()*12:.1f} {-hh*0.8:.0f} '
          f'{-8+_r()*16:.1f} {-hh:.0f}" stroke="#5E7A48" stroke-width="2.6" '
          f'fill="none" stroke-linecap="round" opacity=".8"/></g></g>')

    # ── the near bank ────────────────────────────────────────────────
    a(f'<path d="M0 {BANK+16} C120 {BANK-8} 250 {BANK+4} 360 {BANK-6} '
      f'C470 {BANK-16} 570 {BANK+2} {W} {BANK-8} L{W} 800 L0 800 Z" fill="url(#rvBank)"/>')
    a(f'<path d="M0 {BANK+16} C120 {BANK-8} 250 {BANK+4} 360 {BANK-6} '
      f'C470 {BANK-16} 570 {BANK+2} {W} {BANK-8}" stroke="#A8B578" stroke-width="3" opacity=".55"/>')

    # ── the kadamba tree leaning in over the water ───────────────────
    a('<g class="rv-tree">'
      '<path d="M-14 806 C8 706 26 606 32 506 C36 444 31 384 18 332 L50 324 '
      'C62 380 67 444 64 508 C58 610 42 706 26 806 Z" fill="#6B4A2E"/>'
      '<path d="M-8 640 C10 622 28 614 46 616" stroke="#5C3F26" stroke-width="7" '
      'fill="none" stroke-linecap="round" opacity=".9"/>'
      '<path d="M34 466 C74 446 112 430 158 426 M38 392 C84 376 122 366 166 368" '
      'stroke="#6B4A2E" stroke-width="7" fill="none" stroke-linecap="round"/>')
    for cx, cy, rr in [(40, 252, 74), (124, 294, 58), (174, 348, 44), (102, 356, 42),
                       (12, 322, 54), (166, 292, 38), (74, 200, 50)]:
        a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rr}" ry="{rr*0.76:.0f}" fill="#44633A" opacity=".95"/>')
    for cx, cy, rr in [(52, 236, 48), (132, 286, 34), (170, 340, 28), (22, 302, 34), (90, 194, 31)]:
        a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rr}" ry="{rr*0.72:.0f}" fill="#567A44" opacity=".85"/>')
    for _ in range(30):                       # kadamba blossom
        bx, by = _r() * 196 - 18, 158 + _r() * 212
        a(f'<circle cx="{bx:.0f}" cy="{by:.0f}" r="{3.4 + _r()*3.2:.1f}" fill="#F2C14E" opacity=".9"/>')
    # a few strands that sway on the breeze
    for i in range(8):
        vx, vy = 6 + _r() * 170, 290 + _r() * 86
        vl = 40 + _r() * 46
        a(f'<g class="rv-vine" data-i="{i}" transform="translate({vx:.0f} {vy:.0f})">'
          f'<g class="sw">'
          f'<path d="M0 0 C5 {vl*0.4:.0f} -3 {vl*0.72:.0f} 1 {vl:.0f}" stroke="#44633A" '
          'stroke-width="2.4" fill="none" stroke-linecap="round" opacity=".85"/>'
          f'<ellipse cx="1" cy="{vl+7:.0f}" rx="6" ry="9" fill="#4E6E3E" opacity=".9"/>'
          f'<circle cx="1" cy="{vl+18:.0f}" r="4" fill="#F2C14E" opacity=".85"/>'
          '</g></g>')
    a('</g>')

    # ── fireflies that come out as it darkens ────────────────────────
    for i in range(22):
        fx, fy = 60 + _r() * 560, 420 + _r() * 340
        a(f'<circle class="rv-fly" data-i="{i}" cx="{fx:.0f}" cy="{fy:.0f}" '
          f'r="{5 + _r()*5:.1f}" fill="url(#rvFly)" opacity="0"/>')

    # ── grass in the foreground, and a warm wash for the last act ────
    for i in range(26):
        gx = _r() * W
        gh = 26 + _r() * 46
        a(f'<g class="rv-grass" data-i="{i}" transform="translate({gx:.0f} 806)">'
          f'<g class="sw"><path d="M0 0 C{-5+_r()*10:.1f} {-gh*0.6:.0f} {-8+_r()*16:.1f} {-gh*0.85:.0f} '
          f'{-12+_r()*24:.1f} {-gh:.0f}" stroke="#55703C" stroke-width="3" fill="none" '
          'stroke-linecap="round" opacity=".9"/></g></g>')
    a(f'<rect class="rv-warm" width="{W}" height="800" fill="url(#rvWarm)" opacity="0"/>')
    a('</svg>')
    return ''.join(o)


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
    '<p class="kin">Smt. Vijay Laxmi Sharma</p><p class="kin">Sh. Rajender Dev Sharma</p><p class="kin">Miss Arushi Sharma</p></div>'
    '<div class="fdiv"></div>'
    '<div class="fam"><h3>Groom&rsquo;s Family</h3><p class="deva fsub">वर पक्ष</p>'
    '<p class="kin">Shanti Swaroop Sharma</p><p class="kin">Raksha Sharma</p><p class="kin">Suman Sharma</p><p class="kin">Malini Sharma</p>'
    '<p class="bless">with the blessings of Nana ji<br><b>O. P. Kaushal</b></p></div></div>',

    '<p class="invite">request the pleasure of your company<br>at the wedding of</p>'
    '<p class="name">Smatav</p><p class="deva sub">चि. स्मतव</p>'
    '<p class="weds">weds <span class="deva">एवं</span></p>'
    '<p class="name">Priyanka</p><p class="deva sub">सुश्री प्रियंका</p>'
    '<p class="deva hi-note">इस मंगल अवसर पर आप सपरिवार पधारकर<br>वर-वधू को आशीर्वाद प्रदान करें।</p>',

    '<p class="label">The Celebrations</p><p class="deva sub">समारोह</p>' + ORN +
    '<div class="ev"><div class="evd"><b>29</b><span>November 2026</span><i class="deva">रविवार</i></div>'
    '<div class="evb"><h3>Ladies Sangeet <span class="deva">महिला संगीत</span></h3>'
    '<p class="evx">An evening of dholak, song and dancing.</p>'
    '<p class="evt">Sunday &middot; 4:00 PM onwards</p></div></div>'
    '<div class="ev"><div class="evd"><b>04</b><span>December 2026</span><i class="deva">शुक्रवार</i></div>'
    '<div class="evb"><h3>The Dham <span class="deva">धाम</span></h3>'
    '<p class="evx">The traditional Pahari feast, served to all.</p>'
    '<p class="evt">Friday &middot; 12:00 noon &ndash; 4:00 PM</p></div></div>',

    '<p class="label">Both occasions at</p><p class="deva sub">दोनों कार्यक्रम स्थल</p>'
    '<p class="venue">Lions Club Bhawan</p><p class="deva sub">लायंस क्लब भवन</p>'
    '<p class="addr">Excise Office Road, Chilgari<br>Dharamshala, Himachal Pradesh 176215</p>' + ORN +
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
html,body{width:1920px;height:1080px;overflow:hidden;background:#FBEFE7}
body{font-family:'Cormorant Garamond',Georgia,serif;color:@@ROSE@@;
  background:
    radial-gradient(ellipse at 12% 6%,rgba(224,154,60,.28) 0%,transparent 42%),
    radial-gradient(ellipse at 88% 8%,rgba(216,100,127,.26) 0%,transparent 40%),
    radial-gradient(ellipse at 50% 104%,rgba(216,100,127,.22) 0%,transparent 52%),
    linear-gradient(168deg,#FDF4EE 0%,#F5DAD1 100%);}
.deva{font-family:'Tiro Devanagari Hindi',serif}

#nagL,#nagR{position:absolute;bottom:6px;width:228px;z-index:30}
#nagL{left:2px} #nagR{right:2px}
.nag{width:100%;height:auto;display:block}
#shower{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:40}
.fl{position:absolute;top:0;left:0;will-change:transform,opacity}
.petal{border-radius:60% 60% 50% 50% / 70% 70% 40% 40%}

#intro{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;z-index:20}
#intro .pframe{width:400px}
#intro .inv2{font-size:56px;letter-spacing:.05em;color:@@ROSE@@}
.pframe{position:relative;padding:9px;margin:0 auto;
  background:linear-gradient(168deg,#FBEDC9 0%,#D8B771 52%,#8E6B13 100%);
  border-radius:999px 999px 16px 16px;
  box-shadow:0 18px 40px -16px rgba(142,16,52,.42),0 0 0 1px rgba(142,107,19,.5)}
.pframe::after{content:"";position:absolute;inset:5px;border:1.5px solid rgba(255,255,255,.65);
  border-radius:999px 999px 13px 13px}
.pframe img{display:block;width:100%;height:auto;border-radius:999px 999px 9px 9px}

#stage{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:25}
#book{position:relative;width:1460px;height:880px;perspective:3000px}
#stack{position:absolute;top:8px;right:-9px;bottom:8px;width:11px;z-index:1;
  background:repeating-linear-gradient(90deg,#F3E2DC 0 2px,#E6CEC6 2px 3px);border-radius:0 5px 5px 0;
  box-shadow:2px 0 8px -2px rgba(142,16,52,.3)}
.pg{position:absolute;top:0;height:100%;width:730px;overflow:hidden;
  background:linear-gradient(170deg,#FFFCFA 0%,#FBF0EA 100%);
  box-shadow:0 30px 64px -28px rgba(142,16,52,.45)}
#pL{left:0;border-radius:14px 2px 2px 14px;box-shadow:inset -30px 0 40px -28px rgba(142,16,52,.4),0 30px 64px -28px rgba(142,16,52,.45)}
#pR{left:730px;border-radius:2px 14px 14px 2px;box-shadow:inset 30px 0 40px -28px rgba(142,16,52,.4),0 30px 64px -28px rgba(142,16,52,.45)}
#leaf{position:absolute;top:0;left:730px;width:730px;height:100%;transform-origin:left center;transform-style:preserve-3d;z-index:6}
#leaf .face{position:absolute;inset:0;backface-visibility:hidden;overflow:hidden;
  background:linear-gradient(170deg,#FFFCFA 0%,#FBF0EA 100%)}
#lf{border-radius:2px 14px 14px 2px}
#lb{transform:rotateY(180deg);border-radius:14px 2px 2px 14px}
.sh{position:absolute;inset:0;opacity:0;pointer-events:none}
#shF{background:linear-gradient(90deg,rgba(74,12,34,.72) 0%,rgba(74,12,34,.26) 38%,rgba(74,12,34,0) 72%)}
#shB{background:linear-gradient(270deg,rgba(74,12,34,.68) 0%,rgba(74,12,34,.2) 42%,rgba(74,12,34,0) 76%)}
#uShade{position:absolute;inset:0;opacity:0;pointer-events:none;z-index:5;
  background:linear-gradient(90deg,rgba(74,12,34,.55) 0%,rgba(74,12,34,.16) 40%,rgba(74,12,34,0) 74%)}
#edge{position:absolute;top:0;bottom:0;left:0;width:3px;z-index:8;opacity:0;
  background:linear-gradient(90deg,rgba(255,255,255,.9),rgba(255,255,255,0))}

.photo{position:absolute;inset:0;overflow:hidden}
.river{position:absolute;inset:0;width:100%;height:100%;display:block}
.rk-fg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;will-change:transform}
.rk-fg{transform-origin:50% 86%}
.photo::after{content:"";position:absolute;inset:22px;border:2px solid rgba(255,248,230,.55);border-radius:6px;
  box-shadow:0 0 0 1px rgba(142,107,19,.5) inset}
.photo .vg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 52%,rgba(60,10,28,.3) 100%)}

.inner{position:absolute;inset:26px;border:1.5px solid rgba(168,130,44,.6);border-radius:8px;
  display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;text-align:center;padding:34px 38px}
.inner::before{content:"";position:absolute;inset:8px;border:1px solid rgba(168,130,44,.3);border-radius:5px}

.orn{width:210px;height:44px;margin:0}
.inner>*{margin-top:0}
.spray{width:112px;height:112px}
.cov{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%}
.cov-tl{position:absolute;top:26px;left:26px}
.cov-shubh{font-size:68px;letter-spacing:.1em;color:@@ROSE@@}
.cov-names{font-family:'Great Vibes',cursive;font-size:104px;line-height:1.15;color:@@ROSE@@;margin-top:8px}
.cov-names i{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:.48em;color:@@ROSE2@@}
.cov-date{font-size:30px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:@@ROSE2@@;margin-top:20px}

.inv{font-size:60px;letter-spacing:.05em;color:@@ROSE2@@}
.shloka{font-size:42px;line-height:1.95;color:@@ROSE@@}
.trans{font-size:30px;font-style:italic;line-height:1.55;color:@@INK@@}
.shubh{font-size:70px;letter-spacing:.1em;color:@@ROSE@@}
.label{font-size:24px;letter-spacing:.2em;text-transform:uppercase;font-weight:700;color:@@ROSE2@@}
.sub{font-size:34px;color:@@INK@@}
.fams{display:flex;gap:22px;align-items:flex-start;width:100%;margin-top:8px}
.fam{flex:1}
.fam h3{font-size:21px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:@@ROSE2@@}
.fsub{font-size:27px;color:@@INK@@;margin-top:3px}
.kin{font-size:29px;line-height:1.7;color:@@ROSE@@;white-space:nowrap}
.bless{font-size:24px;font-style:italic;color:@@INK@@;margin-top:16px;line-height:1.5}
.bless b{font-style:normal;color:@@ROSE@@;font-size:1.12em}
.fdiv{width:1px;align-self:stretch;background:linear-gradient(180deg,transparent,rgba(168,130,44,.65),transparent)}
.invite{font-size:36px;font-style:italic;line-height:1.65;color:@@INK@@}
.name{font-family:'Great Vibes',cursive;font-size:144px;line-height:1.02;color:@@ROSE@@}
.weds{font-size:40px;font-style:italic;letter-spacing:.14em;color:@@ROSE2@@}
.weds .deva{font-style:normal;font-size:.76em}
.hi-note{font-size:30px;line-height:1.8;color:@@INK@@}
.ev{display:flex;align-items:stretch;width:100%;border:1.5px solid rgba(168,130,44,.55);
  background:rgba(255,250,248,.88);text-align:left}
.evd{width:186px;flex:none;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:18px 8px;
  background:rgba(224,154,60,.16);border-right:1.5px solid rgba(168,130,44,.5)}
.evd b{font-size:72px;line-height:1;font-weight:500;color:@@ROSE@@}
.evd span{font-size:15px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:@@ROSE2@@;margin-top:9px}
.evd i{font-size:20px;font-style:normal;color:@@INK@@;margin-top:4px}
.evb{padding:18px 22px}
.evb h3{font-size:36px;font-weight:600;color:@@ROSE@@}
.evb h3 .deva{font-weight:400;font-size:.7em;color:@@ROSE2@@;margin-left:10px}
.evx{font-size:27px;font-style:italic;color:@@INK@@;margin-top:5px}
.evt{font-size:22px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;color:@@ROSE@@;margin-top:12px}
.venue{font-size:66px;font-weight:600;color:@@ROSE@@}
.addr{font-size:31px;line-height:1.55;color:@@INK@@}
.blessing{font-size:54px;line-height:1.7;color:@@ROSE@@}
</style></head><body>

<div id="intro">
  <div class="pframe"><img src="@@GREEN@@" alt="Lord Ganesha in green and gold at the family puja"></div>
  <p class="deva inv2">॥ श्री गणेशाय नमः ॥</p>
</div>

<div id="nagL">@@NAGL@@</div><div id="nagR">@@NAGR@@</div>

<div id="stage"><div id="book">
  <div id="stack"></div>
  <div class="pg" id="pL"><div class="photo">@@RIVER@@<img class="rk-fg" src="@@DANCERS@@" alt="Radha and Krishna on the bank of the Yamuna"><div class="vg"></div></div></div>
  <div class="pg" id="pR"><div class="inner" id="iR"></div><div id="uShade"></div></div>
  <div id="leaf">
    <div class="face" id="lf"><div class="inner" id="ilf"></div><div class="sh" id="shF"></div><div id="edge"></div></div>
    <div class="face" id="lb"><div class="photo">@@RIVER@@<img class="rk-fg" src="@@DANCERS@@" alt="Radha and Krishna on the bank of the Yamuna"><div class="vg"></div></div><div class="sh" id="shB"></div></div>
  </div>
</div></div>

<div id="shower"></div>

<script>
const PAGEHTML = @@PAGES@@, TIMES = @@TIMES@@, DURATION = @@DUR@@;
const HOLD = @@HOLD@@, TURN = @@TURN@@, OPEN_DUR = @@OPEN@@, COVER_HOLD = @@COVER_HOLD@@;
const SCENE_B = @@SCENE_B@@, BOOK_IN = SCENE_B - 0.2, BEAT = 60/104, START = TIMES[1];

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
    grass:grab('.rv-grass'),flies:[...sv.querySelectorAll('.rv-fly')].map(el=>({el,i:+el.dataset.i}))};
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
  flakes.push({el,x:rnd()*1960-20,y0:rnd()*1500,sp:(40+rnd()*54)*(0.7+near*0.7),amp:26+rnd()*78,ph:rnd()*6.283,
               spin:(rnd()<.5?-1:1)*(34+rnd()*96),flut:1.4+rnd()*2.2,op:(.5+rnd()*.42)*(0.6+near*0.5)});
}

const iR=document.getElementById('iR'),ilf=document.getElementById('ilf'),
      leaf=document.getElementById('leaf'),shF=document.getElementById('shF'),shB=document.getElementById('shB'),
      uShade=document.getElementById('uShade'),edge=document.getElementById('edge'),
      book=document.getElementById('book'),stage=document.getElementById('stage'),
      intro=document.getElementById('intro'),pL=document.getElementById('pL'),
      nags=[document.getElementById('nagL'),document.getElementById('nagR')],
      dancers=[...document.querySelectorAll('.rk-fg')];
let last={};
const setHTML=(n,k,h)=>{ if(last[k]!==h){n.innerHTML=h;last[k]=h;} };

function seek(t){
  for(const f of flakes){
    const y=((f.y0+t*f.sp)%1460+1460)%1460-190;
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

  /* Radha and Krishna: they come along the bank and meet, stand a while by
     the water, and then dance as the sky turns gold. */
  let cx,cs,cy,cop=1,danceAmt;
  if(t<A2){
    const p=easeIO(clamp((t-START)/(A2-START),0,1));
    cx=300-290*p; cs=0.68+0.02*p; danceAmt=0;
    cy=-5.5*Math.abs(Math.sin(Math.PI*(t-START)/0.62))*(1-0.85*p);   /* the step of a walk */
    cop=clamp((t-START)/1.4,0,1);
  } else if(t<A3){
    const p=easeIO(clamp((t-A2)/(A3-A2),0,1));
    cx=10-10*p; cs=0.70+0.06*p; danceAmt=0;
    cy=-2.4*Math.sin(2*Math.PI*(t-A2)/3.1);                          /* at rest, breathing */
  } else {
    cx=0; cs=0.76+0.10*easeIO(clamp((t-A3)/(DURATION-A3),0,1));
    danceAmt=easeIO(clamp((t-A3)/2.6,0,1)); cy=0;
  }
  /* drop them so their feet meet the bank whatever the scale: the cut-out's
     lowest pixel sits at 722px in the page, the grass line at 761px */
  cy += 17 + 34.8*cs;
  const ph=t/BEAT;
  const bounce=-9.5*Math.abs(Math.sin(Math.PI*ph))*danceAmt;
  const sway=2.3*Math.sin(2*Math.PI*ph/4)*(0.3+0.7*danceAmt);
  const skew=1.1*Math.sin(2*Math.PI*ph/4+0.6)*danceAmt;
  const pulse=1+0.016*Math.abs(Math.sin(Math.PI*ph))*danceAmt;
  const dT='translate('+cx.toFixed(1)+'px,'+(cy+bounce).toFixed(2)+'px) rotate('+sway.toFixed(2)
    +'deg) skewX('+skew.toFixed(2)+'deg) scale('+(cs*pulse).toFixed(4)+')';
  for(const d of dancers){ d.style.transform=dT; d.style.opacity=cop.toFixed(3); }

  const iin=easeOut(clamp(t/1.0,0,1)), iout=1-easeIO(clamp((t-(SCENE_B-0.9))/0.9,0,1));
  intro.style.opacity=(iin*iout).toFixed(3);
  intro.style.transform='scale('+(0.94+0.06*iin).toFixed(4)+')';
  intro.style.visibility=(iin*iout)<0.004?'hidden':'visible';

  const bin=easeOut(clamp((t-BOOK_IN)/1.0,0,1));
  stage.style.opacity=(bin*clamp((DURATION-t)/1.4,0,1)).toFixed(3);
  stage.style.visibility=bin<0.004?'hidden':'visible';
  stage.style.transform='scale('+(1+0.014*Math.sin(t*0.17)).toFixed(4)+')';   /* the camera breathes */

  let i=0; for(let k=0;k<TIMES.length;k++) if(t>=TIMES[k]) i=k;
  const isCover=(i===0), dur=isCover?OPEN_DUR:TURN;
  const tStart=TIMES[i]+(isCover?COVER_HOLD:HOLD);
  let p=(i>=PAGEHTML.length-1)?0:clamp((t-tStart)/dur,0,1);
  const nxt=Math.min(i+1,PAGEHTML.length-1);

  setHTML(ilf,'F',PAGEHTML[i]); setHTML(iR,'R',PAGEHTML[nxt]);

  const e=easeIO(p);
  leaf.style.transform='rotateY('+(-180*e).toFixed(2)+'deg)';
  leaf.style.visibility=(p>=1)?'hidden':'visible';
  const lift=Math.sin(Math.PI*p);
  shF.style.opacity=(0.80*lift).toFixed(3);
  shB.style.opacity=(0.70*clamp((1-p)*2.1,0,1)*(p>0.45?1:0)).toFixed(3);
  uShade.style.opacity=(0.55*lift).toFixed(3);
  edge.style.opacity=(0.75*lift).toFixed(3);

  const closed=isCover?(1-e):0;
  book.style.transform='translateX('+(-365*closed).toFixed(1)+'px)';
  pL.style.opacity=(isCover?e:1).toFixed(3);
}
window.seek=seek; window.DURATION=DURATION; seek(0);
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
