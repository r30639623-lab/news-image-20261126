#!/usr/bin/env python3
"""Render 'The World Today' for Thursday 26 November 2026.

Draws a 1024x1024 newspaper front page with 35 real, verified stories from
26 November 2026 across 7 regions, and writes news.png next to this file.
Pure Pillow drawing: every glyph, chart, map and pin is drawn by this script
from the story data below. Deterministic: no clock, no randomness, no network.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (26, 26, 26)
RED = (163, 18, 30)
RED_DARK = (140, 14, 26)
GREY = (90, 86, 78)
LINE = (60, 56, 48)
PANEL = (232, 226, 210)
SEA = (214, 226, 232)
LAND = (222, 208, 178)
LAND_EDGE = (150, 138, 112)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


TRUNC = []


def draw_wrapped(draw, x, y, s, f, max_w, fill=INK, leading=None, max_lines=None):
    lines = wrap(draw, s, f, max_w)
    if max_lines:
        if len(lines) > max_lines:
            TRUNC.append((s, len(lines), max_lines))
        lines = lines[:max_lines]
    lh = leading if leading else int(f.size * 1.22)
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def rule(draw, x, y, w, width=2, fill=INK):
    draw.line([(x, y), (x + w, y)], fill=fill, width=width)


# ---------------------------------------------------------------- stories
# Every story below happened, or was first reported, on Thu 26 Nov 2026.
# Sources checked 26 Nov 2026: Reuters, BBC, One Turn, Daily Summary Of,
# Newsquawk, ABC (Australia), RNZ, The Standard, MyJoyOnline, Premium Times,
# VolcanoDiscovery/USGS, France 24, NPR, The Hindu.

TICKER = ("US tariffs hit 14 partners  \u00b7  Cairo tanker fire kills 31  "
          "\u00b7  Houthis strike Saudi refinery")

STATS = [
    ("14", "trading partners hit\nby new US tariffs"),
    ("31", "killed in the\nCairo tanker fire"),
    ("5", "jets Kyiv says it hit\nat Savasleyka airbase"),
    ("3.25%", "Bank of Korea rate\nafter a 25bp hike"),
    ("76", "hostages freed\nin Cartagena"),
    ("1m", "satellites cleared\nfor SpaceX"),
]

REGIONS = ("AMERICAS 8 \u00b7 EUROPE 5 \u00b7 MIDDLE EAST 4 \u00b7 ASIA 4 \u00b7 "
           "AFRICA 7 \u00b7 OCEANIA 5 \u00b7 GLOBAL 2")

# Feature cards: (number, tag, city, headline, deck, source, art)
FEATURES = [
    (1, "TARIFFS", "WASHINGTON",
     "US proposes new tariffs on 14 partners",
     "Washington unveils country-specific tariffs on 14 economies, "
     "including China, the EU, Japan and India; Tokyo calls the move regrettable.",
     "BBC \u00b7 Reuters", "bars"),
    (2, "DISASTER", "CAIRO",
     "Fuel tanker fire kills at least 31 in Cairo",
     "A tanker overturns and bursts into flames on the capital's ring road; "
     "31 dead and about 21 hurt, the health ministry says.",
     "Egypt health ministry", "flame"),
    (3, "CONFLICT", "RIYADH",
     "Houthis hit Saudi ports and oil refinery",
     "Yemen's Houthis claim strikes on the Ras Tanura refinery and Saudi "
     "ports; Brent crude climbs as supply fears grow.",
     "Reuters", "refinery"),
]

# Small cards: (number, tag, city, headline, deck, art)
CARDS = [
    (4, "POLITICS", "BRUSSELS",
     "EU leaders clash over \u20ac45bn Ukraine loan",
     "Leaders meet over the \u20ac45bn loan and the 2028\u201334 budget.",
     "chart"),
    (5, "CONFLICT", "KYIV",
     "Ukraine says it hit five jets at Russian airbase",
     "Kyiv says the strike damaged three MiG-31s and two Su-34s.",
     "chart"),
    (6, "POLITICS", "PYONGYANG",
     "Kim orders wider deployment of tactical nukes",
     "North Korea to field tactical nukes in more domains, KCNA says.",
     "globe"),
    (7, "CONFLICT", "GAZA",
     "Israeli strike kills Hamas security chief",
     "Hamas security chief Mohammed Abu al-Ouf is killed in Gaza.",
     "flame"),
    (8, "ECONOMY", "SEOUL",
     "Bank of Korea lifts rate to 3.25%",
     "A 25bp hike in a split decision as the AI chip boom rolls on.",
     "chart"),
    (9, "POLITICS", "TEHRAN",
     "US tells citizens to leave Iran",
     "Washington urges Americans to leave as war fears grow.",
     "globe"),
    (10, "MARKETS", "NEW YORK",
     "AI sell-off drags Nasdaq near bear market",
     "Selling in AI-linked shares goes on; the Nasdaq 100 pulls back from the brink.",
     "chart"),
    (11, "SPACE", "GLOBAL",
     "FCC clears SpaceX for one million satellites",
     "Up to 1m satellites approved for orbital data centres.",
     "sat"),
    (12, "SCIENCE", "INDIAN OCEAN",
     "M5.5 quake shakes off Indonesia",
     "Magnitude 5.5 quake off Sumbawa; no tsunami warning issued.",
     "quake"),
    (13, "POLITICS", "MADRID",
     "Spain heads to snap vote on Sunday",
     "The 29 Nov vote could end S\u00e1nchez's eight years in office.",
     "ballot"),
]

# Map list: (number, place, text, source, lat, lon) -- lat/lon None = no pin
PLACES = [
    (14, "BOGOR", "13 miners trapped in flooded mine", "reports", -6.6, 106.8),
    (15, "SAN JUAN", "Court cancels Luma power deal", "NPR", 18.47, -66.12),
    (16, "HASAKAH", "ISIL suicide attack kills two", "reports", 36.5, 40.75),
    (17, "CARTAGENA", "Police free 76 hostages", "reports", 10.39, -75.51),
    (18, "CANARY IS.", "Migrants near 2,000 in one day", "reports", 28.29, -16.63),
    (19, "LONDON", "Tube strike disrupts London", "reports", 51.5, -0.13),
    (20, "LUSAKA", "Zambia bans protest over term limits", "SRI", -15.39, 28.32),
    (21, "EDO", "Gunmen open fire at Peter Obi rally", "reports", 6.34, 5.63),
    (22, "NAIROBI", "Cult leader convicted again", "Reuters", -1.29, 36.82),
    (23, "CANBERRA", "Australia to miss 2035 target", "Guardian", -35.28, 149.13),
    (24, "FLINDERS IS.", "Bushfire destroys six homes", "reports", -40.0, 148.0),
    (25, "SYDNEY", "Beale returns to the Wallabies", "ABC", -33.87, 151.21),
    (26, "WELLINGTON", "NZ to review $200m gas fund", "RNZ", -41.29, 174.78),
    (27, "CANBERRA", "Secret-zones bill sparks outcry", "Guardian", -35.6, 149.5),
    (28, "WASHINGTON", "Birthright order blocked again", "Reuters", 38.9, -77.04),
    (29, "IOWA", "\u2018Zero\u2019 airborne lead found after blast", "ABC", 41.59, -93.62),
    (30, "WORLD", "Nations urge halt to riot-agent use", "Reuters", None, None),
    (31, "ACCRA", "Power cuts blamed on upgrades", "MyJoyOnline", 5.6, -0.19),
    (32, "NAIROBI", "NCBA profit up 14.6%", "The Standard", -1.6, 37.1),
    (33, "DR CONGO", "Rebels retreat after clashes", "reports", -4.32, 15.31),
    (34, "SANTA CLARA", "Huang returns to Nvidia as CEO", "reports", 37.35, -121.96),
    (35, "BROOKLYN", "Huawei guilty of stealing secrets", "reports", 40.65, -73.95),
]

DATE_CHECK = ("DATE CHECK \u2014 Left out as earlier news: Duran Duran guitarist Andy Taylor "
              "died Mon 23 Nov (announced Wed 25 Nov); Miss Universe was won Tue 24 Nov; "
              "Champions League ties were played Wed 25 Nov; the Macy\u2019s parade "
              "postponement was announced Wed 25 Nov. Every story here happened, or was "
              "first reported, on Thu 26 Nov 2026.")


# ---------------------------------------------------------------- art panels
def art_bars(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 34, 48))
    vals = [0.45, 0.62, 0.55, 0.85, 1.0]
    bw = w // 7
    for i, v in enumerate(vals):
        bx = x + 10 + i * (bw + 6)
        bh = int((h - 22) * v)
        draw.rectangle([bx, y + h - 8 - bh, bx + bw, y + h - 8],
                       fill=RED if i == len(vals) - 1 else (200, 190, 160))
    draw.text((x + w - 34, y + 6), "%", font=font(SERIF_B, 26), fill=(240, 230, 200))


def art_flame(draw, x, y, w, h):
    # Height-aware flame: all points stay inside the (x, y, w, h) panel.
    draw.rectangle([x, y, x + w, y + h], fill=(24, 28, 44))
    cx = x + w // 2
    base = y + h - 3
    top = y + 3
    draw.polygon([(cx, top), (cx + 22, base - 8), (cx + 10, base - 3),
                  (cx + 24, base), (cx - 24, base), (cx - 10, base - 3),
                  (cx - 22, base - 8)], fill=(214, 84, 20))
    mid = top + (base - top) // 2
    draw.polygon([(cx, mid), (cx + 11, base - 4), (cx + 5, base - 2),
                  (cx + 12, base), (cx - 12, base), (cx - 5, base - 2),
                  (cx - 11, base - 4)], fill=(240, 180, 40))


def art_refinery(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(28, 40, 44))
    base = y + h - 6
    for tx, th in [(18, 20), (48, 28), (82, 24)]:
        draw.rectangle([x + tx, base - th, x + tx + 16, base], fill=(200, 190, 160))
        draw.polygon([(x + tx - 2, base - th), (x + tx + 8, base - th - 6),
                      (x + tx + 18, base - th)], fill=(200, 190, 160))
    draw.rectangle([x + 110, base - 14, x + w - 14, base], fill=(180, 170, 140))
    draw.polygon([(x + w - 66, y + h - 16), (x + w - 52, base - 20),
                  (x + w - 44, base - 12), (x + w - 30, base - 20),
                  (x + w - 22, y + h - 16)], fill=(240, 180, 40))


def art_chart(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    pts = [(x + 6 + i * (w - 12) // 6, y + h - 5 - int(v * (h - 10)))
           for i, v in enumerate([0.35, 0.55, 0.42, 0.7, 0.5, 0.82, 0.68])]
    draw.line(pts, fill=RED, width=2)
    for px, py in pts:
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)


def art_globe(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    cx, cy, r = x + w // 2, y + h // 2, min(w, h) // 2 - 3
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 160, 190),
                 outline=INK, width=1)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=INK)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=INK)


def art_sat(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 34, 48))
    cx, cy = x + w // 2, y + h // 2
    draw.rectangle([cx - 16, cy - 4, cx - 4, cy + 4], fill=(120, 160, 190))
    draw.rectangle([cx + 4, cy - 4, cx + 16, cy + 4], fill=(120, 160, 190))
    draw.rectangle([cx - 4, cy - 7, cx + 4, cy + 7], fill=(200, 190, 160))
    for sx, sy in [(x + 10, y + 6), (x + w - 12, y + h - 8), (x + w - 20, y + 8)]:
        draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(240, 230, 200))


def art_quake(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    mid = y + h // 2
    pts = [(x + 4, mid), (x + w // 4, mid), (x + w // 3, mid - 8),
           (x + w // 2, mid + 8), (x + 2 * w // 3, mid - 6),
           (x + 3 * w // 4, mid), (x + w - 4, mid)]
    draw.line(pts, fill=RED, width=2)


def art_ballot(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=PANEL)
    draw.rectangle([x + w // 2 - 14, y + 5, x + w // 2 + 14, y + h - 5],
                   outline=INK, width=2)
    draw.line([(x + w // 2 - 8, y + h // 2), (x + w // 2 - 2, y + h - 8),
               (x + w // 2 + 10, y + 4)], fill=RED, width=2)


ART = {"bars": art_bars, "flame": art_flame, "refinery": art_refinery,
       "chart": art_chart, "globe": art_globe, "sat": art_sat,
       "quake": art_quake, "ballot": art_ballot}


# ---------------------------------------------------------------- map
EURASIA = [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (5, 60),
           (10, 64), (18, 69), (30, 70), (45, 68), (60, 69), (70, 72),
           (80, 73), (90, 75), (100, 76), (110, 74), (120, 73), (130, 72),
           (140, 72), (150, 70), (160, 69), (170, 66), (178, 65), (178, 62),
           (170, 60), (162, 56), (158, 52), (150, 59), (142, 55), (140, 50),
           (135, 45), (130, 42), (127, 40), (122, 38), (120, 32), (122, 28),
           (118, 25), (110, 20), (108, 18), (105, 15), (103, 10), (100, 8),
           (98, 10), (95, 15), (92, 20), (89, 22), (86, 20), (82, 17),
           (80, 13), (77, 8), (75, 12), (73, 16), (70, 20), (66, 25),
           (62, 25), (58, 26), (56, 27), (54, 26), (52, 28), (50, 29),
           (48, 30), (48, 24), (44, 20), (42, 15), (40, 12), (38, 18),
           (35, 28), (34, 28), (35, 31), (36, 36), (30, 36), (27, 37),
           (23, 36), (22, 38), (19, 40), (15, 44), (12, 44), (8, 44),
           (3, 43), (0, 39), (-2, 37), (-6, 36), (-9, 37), (-10, 36)]
N_AMERICA = [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69),
             (-85, 66), (-75, 62), (-65, 60), (-55, 52), (-60, 47),
             (-65, 44), (-70, 42), (-75, 38), (-80, 32), (-81, 26),
             (-84, 30), (-90, 29), (-97, 26), (-97, 19), (-94, 17),
             (-90, 15), (-86, 12), (-83, 9), (-80, 8), (-77, 7), (-79, 9),
             (-82, 10), (-85, 11), (-88, 13), (-90, 14), (-92, 15),
             (-95, 16), (-97, 16), (-100, 18), (-105, 20), (-110, 23),
             (-114, 29), (-117, 33), (-122, 37), (-124, 42), (-124, 48),
             (-130, 54), (-135, 58), (-145, 60), (-155, 58), (-162, 55),
             (-165, 60), (-168, 66)]
S_AMERICA = [(-80, 8), (-77, 4), (-80, -3), (-81, -6), (-80, -12), (-77, -18),
             (-72, -22), (-70, -30), (-72, -38), (-73, -46), (-70, -52),
             (-68, -55), (-65, -55), (-62, -48), (-57, -42), (-52, -38),
             (-48, -30), (-41, -23), (-38, -15), (-35, -9), (-38, -5),
             (-44, -3), (-50, 0), (-55, 4), (-60, 8), (-62, 10), (-68, 11),
             (-72, 12), (-76, 10), (-79, 9), (-80, 8)]
AFRICA = [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-6, 35), (0, 36),
          (10, 37), (11, 34), (20, 32), (25, 32), (30, 31), (32, 31),
          (35, 28), (34, 27), (37, 22), (39, 18), (40, 15), (43, 12),
          (48, 11), (51, 11), (51, 2), (48, -2), (44, -6), (40, -10),
          (40, -15), (36, -20), (35, -26), (32, -29), (28, -33), (26, -34),
          (20, -35), (17, -32), (15, -27), (13, -20), (12, -15), (12, -9),
          (13, -5), (9, -1), (9, 4), (6, 4), (0, 6), (-8, 5), (-13, 8),
          (-17, 12), (-17, 15)]
AUSTRALIA = [(114, -22), (114, -30), (115, -35), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
             (146, -19), (142, -15), (142, -11), (140, -10), (136, -12),
             (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
             (118, -20), (114, -22)]
NZ = [(166, -46), (168, -44), (172, -41), (175, -38), (177, -38),
      (174, -41), (170, -44), (167, -45), (166, -46)]
CONTINENTS = [N_AMERICA, S_AMERICA, AFRICA, EURASIA, AUSTRALIA, NZ]


def draw_map(draw, mx, my, mw, mh):
    draw.rectangle([mx, my, mx + mw, my + mh], fill=SEA, outline=LINE)
    def px(lon):
        return mx + (lon + 180.0) / 360.0 * mw
    def py(lat):
        return my + (72.0 - lat) / 128.0 * mh
    for poly in CONTINENTS:
        pts = [(px(lon), py(lat)) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    f_pin = font(SANS_B, 8)
    for n, _place, _t, _s, lat, lon in PLACES:
        if lat is None:
            continue
        cx, cy = px(lon), py(lat)
        r = 7
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=(255, 255, 255))
        label = str(n)
        tw = draw.textlength(label, font=f_pin)
        draw.text((cx - tw / 2, cy - 5), label, font=f_pin,
                  fill=(255, 255, 255))


# ---------------------------------------------------------------- page
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28                      # side margin
    CW = W - 2 * M              # content width

    # masthead
    y = 14
    f_title = font(SERIF_B, 62)
    t = "THE WORLD TODAY"
    d.text(((W - text_w(d, t, f_title)) / 2, y), t, font=f_title, fill=INK)
    y += 74
    f_date = font(SANS_B, 26)
    t = "THURSDAY, 26 NOVEMBER 2026"
    d.text(((W - text_w(d, t, f_date)) / 2, y), t, font=f_date, fill=INK)
    y += 38
    f_sub = font(SANS_B, 14)
    t = "35 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED THURSDAY 26 NOVEMBER 2026"
    d.text(((W - text_w(d, t, f_sub)) / 2, y), t, font=f_sub, fill=RED)
    y += 24
    f_tick = font(SERIF, 14)
    d.text(((W - text_w(d, TICKER, f_tick)) / 2, y), TICKER, font=f_tick, fill=GREY)
    y += 24
    rule(d, M, y, CW, 2)
    y += 8

    # stat boxes
    box_w = (CW - 5 * 6) // 6
    box_h = 56
    for i, (num, cap) in enumerate(STATS):
        x = M + i * (box_w + 6)
        d.rectangle([x, y, x + box_w, y + box_h], outline=LINE)
        f_num = font(SERIF_B, 26)
        d.text(((x + box_w / 2 - text_w(d, num, f_num) / 2), y + 3),
               num, font=f_num, fill=RED)
        f_cap = font(SANS, 9)
        for j, ln in enumerate(cap.split("\n")):
            d.text(((x + box_w / 2 - text_w(d, ln, f_cap) / 2), y + 32 + j * 11),
                   ln, font=f_cap, fill=GREY)
    y += box_h + 8
    f_reg = font(SANS_B, 14)
    d.text(((W - text_w(d, REGIONS, f_reg)) / 2, y), REGIONS, font=f_reg, fill=INK)
    y += 24
    rule(d, M, y, CW, 2)
    y += 10

    # feature cards
    feat_w = (CW - 2 * 8) // 3
    feat_h = 224
    fy = y
    for i, (n, tag, city, head, deck, src, art) in enumerate(FEATURES):
        x = M + i * (feat_w + 8)
        d.rectangle([x, fy, x + feat_w, fy + feat_h], outline=LINE)
        d.rectangle([x, fy, x + feat_w, fy + 24], fill=RED)
        f_h = font(SANS_B, 12)
        d.text((x + 6, fy + 5), f"{n} {tag}", font=f_h, fill=(255, 255, 255))
        cw = text_w(d, city, f_h)
        d.text((x + feat_w - 6 - cw, fy + 5), city, font=f_h, fill=(255, 255, 255))
        yy = draw_wrapped(d, x + 8, fy + 32, head, font(SERIF_B, 20),
                          feat_w - 16, leading=23, max_lines=3)
        yy = draw_wrapped(d, x + 8, yy + 4, deck, font(SANS, 11),
                          feat_w - 16, leading=14, max_lines=3)
        d.text((x + 8, fy + feat_h - 66), src, font=font(SANS, 10), fill=GREY)
        ART[art](d, x + 1, fy + feat_h - 52, feat_w - 2, 51)
    y = fy + feat_h + 10

    # small cards: 5 cols x 2 rows
    card_w = (CW - 4 * 8) // 5
    card_h = 116
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            n, tag, city, head, deck, art = CARDS[idx]
            x = M + col * (card_w + 8)
            yy = y + row * (card_h + 8)
            d.rectangle([x, yy, x + card_w, yy + card_h], outline=LINE)
            d.rectangle([x, yy, x + card_w, yy + 18], fill=RED)
            f_h = font(SANS_B, 10)
            d.text((x + 5, yy + 3), f"{n} {tag}", font=f_h, fill=(255, 255, 255))
            cw = text_w(d, city, f_h)
            d.text((x + card_w - 5 - cw, yy + 3), city, font=f_h,
                   fill=(255, 255, 255))
            y2 = draw_wrapped(d, x + 6, yy + 22, head, font(SERIF_B, 12),
                              card_w - 12, leading=14, max_lines=3)
            y2 = draw_wrapped(d, x + 6, y2 + 2, deck, font(SANS, 9),
                              card_w - 12, leading=11, max_lines=2)
            ART[art](d, x + 1, yy + card_h - 22, card_w - 2, 21)
    y += 2 * card_h + 8 + 6

    # where it happened
    f_sec = font(SERIF_B, 22)
    d.text((M, y), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    y += 30
    map_x, map_y, map_w, map_h = M, y, 300, 160
    draw_map(d, map_x, map_y, map_w, map_h)
    list_x = map_x + map_w + 12
    col_w = (W - M - list_x - 8) // 2
    f_item = font(SANS, 10)
    f_item_b = font(SANS_B, 10)
    overflow = []
    for i, (n, place, text, src, _la, _lo) in enumerate(PLACES):
        col = i // 11
        rowi = i % 11
        lx = list_x + col * (col_w + 8)
        ly = map_y + rowi * 15
        num = f"{n}. "
        line = f"{num}{place} \u2014 {text} ({src})"
        if text_w(d, line, f_item) > col_w:
            overflow.append((n, line))
        d.text((lx, ly), num, font=f_item_b, fill=RED)
        d.text((lx + text_w(d, num, f_item_b), ly), line[len(num):],
               font=f_item, fill=INK)
    if overflow:
        print("LIST OVERFLOW:", file=sys.stderr)
        for n, line in overflow:
            print(f"  #{n}: {line}", file=sys.stderr)
    if TRUNC:
        print("TEXT TRUNCATED:", file=sys.stderr)
        for s, got, allowed in TRUNC:
            print(f"  {got} lines, max {allowed}: {s}", file=sys.stderr)
    y = map_y + map_h + 10

    # date check + footer
    box_h = 34
    d.rectangle([M, y, W - M, y + box_h], outline=RED, width=2)
    f_dc = font(SANS, 9)
    draw_wrapped(d, M + 8, y + 4, DATE_CHECK, f_dc, CW - 16, leading=12,
                 max_lines=2)
    y += box_h + 6
    f_foot = font(SANS, 10)
    t = "Compiled from major wire reports \u00b7 26 November 2026 \u00b7 PAGE 1 OF 1"
    d.text(((W - text_w(d, t, f_foot)) / 2, y), t, font=f_foot, fill=GREY)
    y += 16
    assert y <= H, f"page overflow: final y={y}"
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "news.png")
    img = build()
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
