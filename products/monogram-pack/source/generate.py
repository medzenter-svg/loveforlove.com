#!/usr/bin/env python3
"""Generate the Monogram & Crest Pack (loveforlove.com) — 12 monogram card designs
   as a print-ready PDF, plus a branded marketing preview-grid PNG."""
import asyncio
import os
from playwright.async_api import async_playwright

PALETTE = {
    "bg": "#F7F3ED",
    "bg2": "#F1E9DE",
    "line": "#DED4C7",
    "ink": "#181716",
    "wine": "#6F252A",
    "gold": "#B79A63",
}

BRANDMARK = '<div class="brandmark">Designed by loveforlove.com</div>'

NAMES = "Emma & James"
INITIALS = ("E", "J")
DATE = "08.21.27"

CARD_W = 340
CARD_H = 300

# ---------------------------------------------------------------- icons ----

def icon_wreath(color):
    leaves = []
    import math
    for side in (-1, 1):
        for i in range(7):
            t = i / 6
            ang = math.radians(20 + t * 140) * side
            r = 34
            x = 45 + side * math.sin(ang) * -1 * 0 + side * (10 + t * 26)
            y = 6 + t * 30
            rot = side * (30 + t * 55)
            leaves.append(
                f'<line x1="{45+side*8}" y1="{y}" x2="{45+side*(8+9)}" y2="{y-4}" '
                f'stroke="{color}" stroke-width="1.4" stroke-linecap="round" '
                f'transform="rotate({rot} {45+side*8} {y})"/>'
            )
    return f'''<svg width="90" height="46" viewBox="0 0 90 46">
      <g>{"".join(leaves)}</g>
      <circle cx="45" cy="6" r="1.6" fill="{color}"/>
    </svg>'''


def icon_rings(color):
    return f'''<svg width="46" height="28" viewBox="0 0 46 28">
      <circle cx="16" cy="14" r="11" fill="none" stroke="{color}" stroke-width="1.6"/>
      <circle cx="30" cy="14" r="11" fill="none" stroke="{color}" stroke-width="1.6"/>
    </svg>'''


def icon_glasses(color):
    def glass(x):
        return f'''
          <path d="M{x},0 L{x+16},0 L{x+8},15 Z" fill="none" stroke="{color}" stroke-width="1.3"/>
          <line x1="{x+8}" y1="15" x2="{x+8}" y2="30" stroke="{color}" stroke-width="1.3"/>
          <line x1="{x+2}" y1="30" x2="{x+14}" y2="30" stroke="{color}" stroke-width="1.3"/>
          <circle cx="{x+5}" cy="-4" r="1" fill="{color}"/>
          <circle cx="{x+10}" cy="-7" r="1" fill="{color}"/>
        '''
    return f'''<svg width="60" height="40" viewBox="-4 -10 68 44">
      {glass(0)}{glass(28)}
    </svg>'''


def icon_chapel(color):
    return f'''<svg width="46" height="46" viewBox="0 0 46 46">
      <polygon points="23,2 43,20 3,20" fill="none" stroke="{color}" stroke-width="1.3"/>
      <rect x="8" y="20" width="30" height="24" fill="none" stroke="{color}" stroke-width="1.3"/>
      <rect x="19" y="30" width="8" height="14" fill="none" stroke="{color}" stroke-width="1.3"/>
      <line x1="23" y1="2" x2="23" y2="-4" stroke="{color}" stroke-width="1.3"/>
      <line x1="20" y1="-1" x2="26" y2="-1" stroke="{color}" stroke-width="1.3"/>
    </svg>'''


def icon_branch(color):
    leaves = "".join(
        f'<ellipse cx="{14+i*9}" cy="{6 if i%2==0 else 14}" rx="6" ry="3" '
        f'fill="none" stroke="{color}" stroke-width="1.1" '
        f'transform="rotate({-25 if i%2==0 else 25} {14+i*9} {6 if i%2==0 else 14})"/>'
        for i in range(6)
    )
    return f'''<svg width="80" height="26" viewBox="0 0 80 26">
      <line x1="4" y1="12" x2="76" y2="12" stroke="{color}" stroke-width="1.1"/>
      {leaves}
    </svg>'''


# ---------------------------------------------------------------- variants --

def frame(inner, bg=PALETTE["bg"], border=PALETTE["gold"]):
    return f'''<div class="card" style="background:{bg};">
      <div class="cf" style="border-color:{border};"></div>
      <div class="cfi"></div>
      <div class="cc">{inner}</div>
    </div>'''


def v_wreath():
    return frame(f'''
      {icon_wreath(PALETTE["gold"])}
      <div class="ini">{INITIALS[0]} &amp; {INITIALS[1]}</div>
      <div class="nm-small">{NAMES.upper()}</div>
      <div class="dt">{DATE}</div>
    ''')


def v_framed_floral():
    return frame(f'''
      <div class="corner tl">&#10058;</div><div class="corner tr">&#10058;</div>
      <div class="kicker">TOGETHER WITH THEIR FAMILIES</div>
      <div class="nm">OLIVIA<br/><i>and</i><br/>NICHOLAS</div>
      <div class="dt">{DATE}</div>
    '''.replace("OLIVIA<br/><i>and</i><br/>NICHOLAS", f'{NAMES.split(" & ")[0].upper()}<br/><i>and</i><br/>{NAMES.split(" & ")[1].upper()}'))


def v_bigslash():
    return frame(f'''
      <div class="ini-big">{INITIALS[0]}<span class="slash">/</span>{INITIALS[1]}</div>
      <div class="rule"></div>
      <div class="nm-small">{NAMES.upper()}</div>
    ''')


def v_rings():
    return frame(f'''
      {icon_rings(PALETTE["gold"])}
      <div class="nm">{NAMES.split(" & ")[0].upper()}<br/><i>and</i><br/>{NAMES.split(" & ")[1].upper()}</div>
      <div class="dt">{DATE}</div>
    ''')


def v_arch():
    inner = f'''
      <div class="arch-shape"></div>
      <div class="arch-inner">
        <div class="ini">{INITIALS[0]} &amp; {INITIALS[1]}</div>
        <div class="dt">{DATE}</div>
      </div>
    '''
    return frame(inner)


def v_glasses():
    return frame(f'''
      {icon_glasses(PALETTE["wine"])}
      <div class="kicker" style="margin-top:8px;">CHEERS TO LOVE</div>
      <div class="nm-small">{NAMES.upper()}</div>
    ''')


def v_oval():
    inner = f'''
      <div class="oval-shape"></div>
      <div class="oval-inner">
        <div class="nm-small">{NAMES.upper()}</div>
        <div class="dt">{DATE}</div>
      </div>
    '''
    return frame(inner)


def v_clean_rect():
    return frame(f'''
      <div class="rect-inner">
        <div class="nm-small" style="letter-spacing:2px;">{NAMES.upper()}</div>
        <div class="dt">{DATE}</div>
      </div>
    ''')


def v_inverted():
    inner = f'''
      <div class="ini" style="color:{PALETTE['bg']};">{INITIALS[0]} &amp; {INITIALS[1]}</div>
      <div class="dt" style="color:{PALETTE['gold']};">{DATE}</div>
    '''
    return frame(inner, bg=PALETTE["ink"], border=PALETTE["gold"])


def v_floral_branch():
    return frame(f'''
      {icon_branch(PALETTE["gold"])}
      <div class="nm-small" style="margin-top:10px;">{NAMES.upper()}</div>
      <div class="dt">{DATE}</div>
    ''')


def v_chapel():
    return frame(f'''
      {icon_chapel(PALETTE["ink"])}
      <div class="nm-small">{NAMES.upper()}</div>
      <div class="dt">{DATE}</div>
    ''')


def v_seal():
    inner = f'''
      <div class="seal-shape"></div>
      <div class="seal-inner">{INITIALS[0]}<span class="dot">&middot;</span>{INITIALS[1]}</div>
    '''
    return frame(inner, bg=PALETTE["bg2"])


VARIANTS = [
    ("Wreath Monogram", v_wreath),
    ("Framed Floral", v_framed_floral),
    ("Bold Initial Slash", v_bigslash),
    ("Interlocking Rings", v_rings),
    ("Arch Frame", v_arch),
    ("Champagne Toast", v_glasses),
    ("Oval Frame", v_oval),
    ("Classic Rectangle", v_clean_rect),
    ("Ink & Gold", v_inverted),
    ("Floral Branch", v_floral_branch),
    ("Chapel Silhouette", v_chapel),
    ("Wax Seal Initials", v_seal),
]

STYLE = f"""
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:'Poppins', sans-serif; background:{PALETTE['bg']}; }}

  .card {{ width:{CARD_W}px; height:{CARD_H}px; position:relative; }}
  .cf {{ position:absolute; top:10px; left:10px; right:10px; bottom:10px; border:1px solid; }}
  .cfi {{ position:absolute; top:15px; left:15px; right:15px; bottom:15px; border:1px solid {PALETTE['line']}; }}
  .cc {{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center;
         justify-content:center; text-align:center; padding:0 28px; }}

  .kicker {{ font-size:9px; letter-spacing:3px; color:{PALETTE['wine']}; margin-bottom:10px; }}
  .nm {{ font-family:'Lora', serif; font-size:19px; color:{PALETTE['ink']}; line-height:1.5; font-weight:600; }}
  .nm i {{ font-style:italic; font-weight:400; font-size:13px; color:#7a6f63; }}
  .nm-small {{ font-family:'Lora', serif; font-size:14px; color:{PALETTE['ink']}; letter-spacing:1px; font-weight:600; margin-top:4px; }}
  .dt {{ font-size:9.5px; letter-spacing:2px; color:#8a7a6d; margin-top:8px; }}
  .ini {{ font-family:'Lora', serif; font-size:34px; color:{PALETTE['ink']}; font-weight:600; margin-top:4px; }}
  .ini-big {{ font-family:'Lora', serif; font-size:48px; color:{PALETTE['ink']}; font-weight:600; }}
  .slash {{ color:{PALETTE['gold']}; margin:0 6px; font-weight:300; }}
  .rule {{ width:50px; height:1px; background:{PALETTE['gold']}; margin:14px auto; }}
  .corner {{ position:absolute; font-size:14px; color:{PALETTE['gold']}; }}
  .corner.tl {{ top:22px; left:22px; }}
  .corner.tr {{ top:22px; right:22px; }}

  .arch-shape {{ position:absolute; top:24px; left:50%; transform:translateX(-50%);
                 width:170px; height:170px; border:1px solid {PALETTE['gold']};
                 border-top-left-radius:90px; border-top-right-radius:90px; border-bottom:none; }}
  .arch-inner {{ position:relative; z-index:1; margin-top:20px; }}

  .oval-shape {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
                 width:230px; height:150px; border:1px solid {PALETTE['gold']}; border-radius:50%; }}
  .oval-inner {{ position:relative; z-index:1; }}

  .rect-inner {{ border:1px solid {PALETTE['gold']}; padding:20px 26px; }}

  .seal-shape {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
                 width:120px; height:120px; border-radius:50%; border:2px solid {PALETTE['wine']}; }}
  .seal-inner {{ position:relative; z-index:1; font-family:'Lora', serif; font-size:30px;
                 color:{PALETTE['wine']}; font-weight:600; }}
  .seal-inner .dot {{ color:{PALETTE['gold']}; margin:0 4px; }}

  .brandmark {{ position:absolute; bottom:6px; left:0; right:0; text-align:center;
                font-size:6.5px; letter-spacing:1.3px; color:#b4a99b; text-transform:uppercase; }}

  /* cover page */
  .cover-page {{ width:{CARD_W}px; height:{CARD_H}px; position:relative; background:{PALETTE['bg']};
                 display:flex; align-items:center; justify-content:center; }}
  .cover-frame {{ text-align:center; }}
  .cover-kicker {{ font-size:9px; letter-spacing:3px; color:{PALETTE['wine']}; margin-bottom:10px; }}
  .cover-title {{ font-family:'Lora', serif; font-size:26px; color:{PALETTE['ink']}; font-weight:600; line-height:1.3; }}
  .cover-sub {{ margin-top:10px; font-size:10.5px; color:#7a6f63; font-style:italic; font-family:'Lora',serif; }}

  /* logo lockup (used on marketing preview) */
  .logo-wrap {{ text-align:center; padding-top:46px; }}
  .logo-word {{ font-family:'Lora', serif; font-size:52px; letter-spacing:16px; color:{PALETTE['ink']};
                font-weight:600; margin-top:14px; }}
  .logo-rule {{ width:80px; height:1px; background:{PALETTE['gold']}; margin:18px auto; }}
  .logo-sub {{ font-size:15px; letter-spacing:2px; color:{PALETTE['wine']}; }}

  /* preview grid */
  .sheet {{ width:1600px; background:{PALETTE['bg']}; padding-bottom:60px; }}
  .grid {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:22px; padding:40px 60px 0; }}
  .tile {{ position:relative; }}
  .tile .num {{ text-align:center; margin-top:8px; font-family:'Lora', serif; font-size:14px; color:#8a7a6d; }}
  .features {{ display:flex; justify-content:center; gap:70px; margin-top:50px; padding:0 60px; }}
  .feat {{ text-align:center; width:200px; }}
  .feat .flabel {{ font-size:11px; letter-spacing:1.5px; color:{PALETTE['ink']}; font-weight:600; margin-top:10px; }}
  .feat .fdesc {{ font-size:9.5px; color:#8a7a6d; margin-top:4px; line-height:1.4; }}
</style>
"""


def cover_page():
    return f'''<div class="cover-page">
      <div class="cover-frame">
        {icon_wreath(PALETTE["gold"])}
        <div class="cover-kicker">A LOVEFORLOVE.COM ORIGINAL</div>
        <div class="cover-title">Monogram<br/>&amp; Crest Pack</div>
        <div class="cover-sub">12 minimalist designs for your wedding suite</div>
      </div>
      {BRANDMARK}
    </div>'''


def feat_icon_download():
    return f'''<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{PALETTE['gold']}" stroke-width="1.4">
      <path d="M12 3v12M7 10l5 5 5-5M4 19h16"/></svg>'''

def feat_icon_edit():
    return f'''<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{PALETTE['gold']}" stroke-width="1.4">
      <path d="M4 20h4L18 10l-4-4L4 16v4z"/></svg>'''

def feat_icon_globe():
    return f'''<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{PALETTE['gold']}" stroke-width="1.4">
      <circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14 0 18M12 3c-3 3.5-3 14 0 18"/></svg>'''

def feat_icon_gem():
    return f'''<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{PALETTE['gold']}" stroke-width="1.4">
      <path d="M6 3h12l3 6-9 12L3 9z"/><path d="M3 9h18M9 3l-3 6 6 12 6-12-3-6"/></svg>'''


def preview_sheet_html():
    tiles = "".join(
        f'<div class="tile">{fn()}<div class="num">{i+1:02d} &middot; {label}</div></div>'
        for i, (label, fn) in enumerate(VARIANTS)
    )
    features = f'''
      <div class="features">
        <div class="feat">{feat_icon_download()}<div class="flabel">INSTANT DOWNLOAD</div><div class="fdesc">Get your files right after purchase</div></div>
        <div class="feat">{feat_icon_edit()}<div class="flabel">EDIT &amp; PRINT</div><div class="fdesc">Easy to customize at home or in print</div></div>
        <div class="feat">{feat_icon_globe()}<div class="flabel">MULTI-LANGUAGE</div><div class="fdesc">Templates ready for guests worldwide</div></div>
        <div class="feat">{feat_icon_gem()}<div class="flabel">PREMIUM DESIGN</div><div class="fdesc">Crafted with love for unforgettable moments</div></div>
      </div>
    '''
    return f'''<div class="sheet">
      <div class="logo-wrap">
        {icon_wreath(PALETTE["gold"])}
        <div class="logo-word">LOVE FOR LOVE</div>
        <div class="logo-rule"></div>
        <div class="logo-sub">12 minimalist monogram designs</div>
      </div>
      <div class="grid">{tiles}</div>
      {features}
    </div>'''


async def main():
    from pypdf import PdfWriter, PdfReader

    pages_html = [cover_page()] + [frame_html for _, fn in VARIANTS for frame_html in [fn() + BRANDMARK]]
    # wrap each in a full page div
    page_htmls = [cover_page()]
    for _, fn in VARIANTS:
        page_htmls.append(f'<div class="page-wrap" style="width:{CARD_W}px;height:{CARD_H}px;">{fn()}{BRANDMARK}</div>')

    with open("preview.html", "w") as f:
        f.write(f"<html><head><meta charset='utf-8'>{STYLE}</head><body>{preview_sheet_html()}</body></html>")

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        page = await browser.new_page()

        pdf_files = []
        for i, html in enumerate(page_htmls):
            fname = f"page_{i}.html"
            with open(fname, "w") as f:
                f.write(f"<html><head><meta charset='utf-8'>{STYLE}</head><body>{html}</body></html>")
            await page.goto(f"file://{os.path.abspath(fname)}")
            out = f"page_{i}.pdf"
            await page.pdf(path=out, width=f"{CARD_W}px", height=f"{CARD_H}px", print_background=True,
                            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            pdf_files.append(out)

        # preview grid screenshot
        await page.goto(f"file://{os.path.abspath('preview.html')}")
        sheet_height = await page.evaluate("document.querySelector('.sheet').scrollHeight")
        await page.set_viewport_size({"width": 1600, "height": int(sheet_height) + 20})
        await page.screenshot(path="Monogram_Pack_Preview_loveforlove.png", full_page=True)

        await browser.close()

    writer = PdfWriter()
    for fname in pdf_files:
        reader = PdfReader(fname)
        for pg in reader.pages:
            writer.add_page(pg)
    with open("Monogram_Crest_Pack_loveforlove.pdf", "wb") as f:
        writer.write(f)

asyncio.run(main())
print("done")
