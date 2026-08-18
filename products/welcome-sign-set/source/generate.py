#!/usr/bin/env python3
"""Generate the Welcome Sign & Guest Book Sign set (loveforlove.com) — 4 style variants
   x 2 signs (Welcome + Guest Book) as a large-format print-ready PDF, plus a branded
   marketing preview-grid PNG."""
import asyncio
import os
from playwright.async_api import async_playwright

PALETTE = {
    "bg": "#F7F3ED", "bg2": "#F1E9DE", "line": "#DED4C7",
    "ink": "#181716", "wine": "#6F252A", "gold": "#B79A63", "cream": "#F7F3ED",
}
BRANDMARK = '<div class="brandmark">Designed by loveforlove.com</div>'
NAMES = "Emma &amp; James"
DATE = "The Fourteenth of June, Twenty Twenty-Seven"
PLACE = "LAKE COMO &middot; ITALY"

SIGN_W = 18  # inches
SIGN_H = 24  # inches
TILE_W = 300
TILE_H = 400


def branch(color):
    return f'''<svg width="90" height="30" viewBox="0 0 90 30" fill="none">
      <path d="M2 15 Q30 4 88 15" stroke="{color}" stroke-width="1"/>
      <ellipse cx="20" cy="10" rx="4" ry="2.2" fill="{color}" transform="rotate(-25 20 10)"/>
      <ellipse cx="34" cy="6" rx="4" ry="2.2" fill="{color}" transform="rotate(-10 34 6)"/>
      <ellipse cx="50" cy="6" rx="4" ry="2.2" fill="{color}" transform="rotate(10 50 6)"/>
      <ellipse cx="66" cy="9" rx="4" ry="2.2" fill="{color}" transform="rotate(22 66 9)"/>
      <ellipse cx="78" cy="14" rx="4" ry="2.2" fill="{color}" transform="rotate(35 78 14)"/>
    </svg>'''


VARIANTS = [
    {
        "key": "classic",
        "label": "Classic Ivory &amp; Gold",
        "bg": PALETTE["bg"], "border": PALETTE["gold"], "border2": PALETTE["line"],
        "ink": PALETTE["ink"], "accent": PALETTE["wine"], "sub": "#7a6f63",
        "deco": "frame",
    },
    {
        "key": "wine",
        "label": "Wine &amp; Gold Elegant",
        "bg": PALETTE["wine"], "border": PALETTE["gold"], "border2": "#8a4650",
        "ink": PALETTE["cream"], "accent": PALETTE["gold"], "sub": "#D8C3AE",
        "deco": "frame",
    },
    {
        "key": "botanical",
        "label": "Botanical Line Art",
        "bg": PALETTE["bg2"], "border": PALETTE["gold"], "border2": PALETTE["line"],
        "ink": PALETTE["ink"], "accent": PALETTE["wine"], "sub": "#7a6f63",
        "deco": "branch",
    },
    {
        "key": "arch",
        "label": "Arch Frame Minimal",
        "bg": PALETTE["bg"], "border": PALETTE["line"], "border2": PALETTE["line"],
        "ink": PALETTE["ink"], "accent": PALETTE["wine"], "sub": "#7a6f63",
        "deco": "arch",
    },
]

STYLE = f"""
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:'Poppins', sans-serif; }}
  .sign {{ width:{SIGN_W}in; height:{SIGN_H}in; position:relative; display:flex;
           align-items:center; justify-content:center; text-align:center; }}
  .frame {{ position:absolute; top:0.7in; left:0.7in; right:0.7in; bottom:0.7in;
            border:2px solid var(--border); }}
  .frame-inner {{ position:absolute; top:0.85in; left:0.85in; right:0.85in; bottom:0.85in;
                  border:1px solid var(--border2); }}
  .arch {{ position:absolute; top:0.7in; left:1.4in; right:1.4in; bottom:0.7in;
           border:2px solid var(--border); border-bottom:none;
           border-radius: 4.5in 4.5in 0 0; }}
  .arch-inner {{ position:absolute; top:0.85in; left:1.55in; right:1.55in; bottom:0.85in;
                 border:1px solid var(--border2); border-bottom:none;
                 border-radius: 4.3in 4.3in 0 0; }}
  .content {{ width:12.5in; z-index:2; }}
  .top-orn {{ margin-bottom:34px; }}
  .top-orn svg {{ width:64px; height:64px; }}
  .kicker {{ font-family:'Lora', serif; font-style:italic; font-size:42px; color:var(--accent);
             margin-bottom:14px; }}
  .headline {{ font-family:'Lora', serif; font-size:128px; font-weight:600; color:var(--ink);
               line-height:1.12; margin-bottom:10px; }}
  .rule {{ width:180px; height:1px; background:var(--border); margin: 44px auto; }}
  .sub {{ font-size:26px; color:var(--sub); max-width:9.6in; margin:0 auto; line-height:1.75; }}
  .names {{ font-family:'Lora', serif; font-size:46px; color:var(--ink); margin-top:38px; }}
  .date {{ font-size:19px; letter-spacing:4px; color:var(--sub); text-transform:uppercase;
           margin-top:18px; }}
  .place {{ font-size:16px; letter-spacing:4px; color:var(--sub); text-transform:uppercase;
            margin-top:8px; }}
  .branch-row {{ display:flex; justify-content:center; gap:36px; margin: 30px 0; }}
  .branch-row svg {{ width:150px; height:auto; }}
  .branch-row svg:last-child {{ transform: scaleX(-1); }}
  .bottom-orn {{ margin-top:46px; display:flex; align-items:center; justify-content:center; gap:18px; }}
  .bottom-orn .bl {{ width:70px; height:1px; background:var(--border); }}
  .bottom-orn .bd {{ font-size:14px; color:var(--accent); }}

  .brandmark {{ position:absolute; bottom:0.35in; left:0; right:0; text-align:center;
                font-size:11px; letter-spacing:2.5px; color:var(--sub); opacity:0.6;
                text-transform:uppercase; }}

  /* preview grid */
  .sheet {{ width:1280px; padding:70px 60px 60px; background:{PALETTE['bg']};
            font-family:'Poppins', sans-serif; }}
  .logo-wrap {{ text-align:center; margin-bottom:48px; }}
  .logo-word {{ font-family:'Lora', serif; font-size:34px; letter-spacing:10px;
                color:{PALETTE['ink']}; margin-top:10px; }}
  .logo-rule {{ width:70px; height:1px; background:{PALETTE['gold']}; margin:16px auto; }}
  .logo-sub {{ font-size:13px; letter-spacing:3px; color:{PALETTE['wine']};
               text-transform:uppercase; }}
  .grid {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:26px; }}
  .tile {{ position:relative; border-radius:6px; overflow:hidden;
           box-shadow: 0 6px 18px rgba(24,23,22,0.12); background:#fff; }}
  .tile img {{ width:100%; display:block; }}
  .tile .cap {{ padding:12px 10px; text-align:center; font-size:12px; letter-spacing:1.5px;
                text-transform:uppercase; color:{PALETTE['ink']}; background:#fff; }}
  .features {{ display:flex; justify-content:space-between; margin-top:56px;
               padding-top:36px; border-top:1px solid {PALETTE['line']}; }}
  .feat {{ text-align:center; width:22%; }}
  .feat svg {{ width:30px; height:30px; }}
  .feat .t {{ font-size:11px; letter-spacing:2px; text-transform:uppercase;
              color:{PALETTE['ink']}; margin-top:10px; font-weight:600; }}
</style>
"""


def sign_html(v, kind):
    css_vars = f"--border:{v['border']}; --border2:{v['border2']}; --ink:{v['ink']}; --accent:{v['accent']}; --sub:{v['sub']};"
    deco = v["deco"]
    if deco == "arch":
        frame_html = '<div class="arch"></div><div class="arch-inner"></div>'
    else:
        frame_html = '<div class="frame"></div><div class="frame-inner"></div>'

    branch_html = f'<div class="branch-row">{branch(v["accent"])}{branch(v["accent"])}</div>' if deco == "branch" else ""
    top_orn = f'<div class="top-orn">{wreath_icon(v["accent"])}</div>'
    bottom_orn = '<div class="bottom-orn"><div class="bl"></div><div class="bd">&#10022;</div><div class="bl"></div></div>'

    if kind == "welcome":
        body = f'''
          {top_orn}
          <div class="kicker">Welcome to the wedding of</div>
          <div class="headline">Emma &amp; James</div>
          {branch_html}
          <div class="rule"></div>
          <div class="sub">We are so happy to share this day with the people we love most.
          Please find your seat, raise a glass, and celebrate with us.</div>
          <div class="date">{DATE}</div>
          <div class="place">{PLACE}</div>
          {bottom_orn}
        '''
    else:
        body = f'''
          {top_orn}
          <div class="kicker">Please</div>
          <div class="headline">Sign Our<br/>Guestbook</div>
          {branch_html}
          <div class="rule"></div>
          <div class="sub">Leave us your best wishes, a favorite memory, or a little advice
          for our new life together — we&rsquo;ll treasure reading these for years to come.</div>
          <div class="names">Emma &amp; James</div>
          {bottom_orn}
        '''

    return f'''<div class="sign" style="background:{v['bg']}; {css_vars}">
      {frame_html}
      <div class="content">{body}</div>
      {BRANDMARK}
    </div>'''


def cover_tile_label(v, kind):
    name = "Welcome Sign" if kind == "welcome" else "Guest Book Sign"
    return f"{v['label'].replace('&amp;','&')} &middot; {name}"


def feat_icon_download():
    return '''<svg viewBox="0 0 24 24" fill="none" stroke="#181716" stroke-width="1.4">
      <path d="M12 3v12M7 10l5 5 5-5M5 20h14"/></svg>'''


def feat_icon_edit():
    return '''<svg viewBox="0 0 24 24" fill="none" stroke="#181716" stroke-width="1.4">
      <path d="M4 20h4L18.5 9.5a2 2 0 000-2.8l-1.2-1.2a2 2 0 00-2.8 0L4 15v5z"/></svg>'''


def feat_icon_globe():
    return '''<svg viewBox="0 0 24 24" fill="none" stroke="#181716" stroke-width="1.4">
      <circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>'''


def feat_icon_gem():
    return '''<svg viewBox="0 0 24 24" fill="none" stroke="#181716" stroke-width="1.4">
      <path d="M6 3h12l3 6-9 12L3 9l3-6z"/><path d="M3 9h18M9 3l3 6 3-6M12 9v12"/></svg>'''


def wreath_icon(color=PALETTE["gold"]):
    import math
    lines = []
    for i in range(24):
        a = (i / 24) * 2 * math.pi
        x1, y1 = 30 + 20 * math.cos(a), 30 + 20 * math.sin(a)
        x2, y2 = 30 + 26 * math.cos(a), 30 + 26 * math.sin(a)
        lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1"/>')
    return f'<svg width="46" height="46" viewBox="0 0 60 60">{"".join(lines)}</svg>'


def preview_sheet_html(tile_srcs):
    tiles = "".join(
        f'<div class="tile"><img src="{src}"/><div class="cap">{cover_tile_label(v, kind)}</div></div>'
        for (v, kind), src in tile_srcs
    )
    features = f'''<div class="features">
      <div class="feat">{feat_icon_download()}<div class="t">Instant Download</div></div>
      <div class="feat">{feat_icon_edit()}<div class="t">Edit &amp; Print</div></div>
      <div class="feat">{feat_icon_globe()}<div class="t">Multi-Language</div></div>
      <div class="feat">{feat_icon_gem()}<div class="t">Premium Design</div></div>
    </div>'''
    return f'''<div class="sheet">
      <div class="logo-wrap">{wreath_icon()}
        <div class="logo-word">LOVE FOR LOVE</div>
        <div class="logo-rule"></div>
        <div class="logo-sub">Welcome &amp; Guest Book Sign &middot; 4 style variants</div>
      </div>
      <div class="grid">{tiles}</div>
      {features}
    </div>'''


async def main():
    from pypdf import PdfWriter, PdfReader

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        page = await browser.new_page()

        pdf_files = []
        tile_srcs = []
        for v in VARIANTS:
            for kind in ("welcome", "guestbook"):
                html = f"<html><head><meta charset='utf-8'>{STYLE}</head><body>{sign_html(v, kind)}</body></html>"
                fname_html = f"{v['key']}_{kind}.html"
                with open(fname_html, "w") as f:
                    f.write(html)
                await page.goto(f"file://{os.path.abspath(fname_html)}")
                fname_pdf = f"{v['key']}_{kind}.pdf"
                await page.pdf(path=fname_pdf, width=f"{SIGN_W}in", height=f"{SIGN_H}in",
                                print_background=True,
                                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
                pdf_files.append(fname_pdf)

                # thumbnail screenshot for marketing sheet
                await page.set_viewport_size({"width": TILE_W, "height": TILE_H})
                thumb_html = f"""<html><head><meta charset='utf-8'>
                  <style>body{{margin:0;}} .sign{{transform:scale({TILE_W/(SIGN_W*96)});
                  transform-origin: top left; width:{SIGN_W*96}px; height:{SIGN_H*96}px;}}</style>
                  {STYLE}</head><body>{sign_html(v, kind)}</body></html>"""
                fname_thumb_html = f"{v['key']}_{kind}_thumb.html"
                with open(fname_thumb_html, "w") as f:
                    f.write(thumb_html)
                await page.goto(f"file://{os.path.abspath(fname_thumb_html)}")
                fname_thumb_png = f"{v['key']}_{kind}_thumb.png"
                await page.screenshot(path=fname_thumb_png, clip={"x": 0, "y": 0, "width": TILE_W, "height": TILE_H})
                tile_srcs.append(((v, kind), fname_thumb_png))

        # marketing preview sheet
        await page.set_viewport_size({"width": 1280, "height": 800})
        preview_html = f"<html><head><meta charset='utf-8'>{STYLE}</head><body>{preview_sheet_html(tile_srcs)}</body></html>"
        with open("preview.html", "w") as f:
            f.write(preview_html)
        await page.goto(f"file://{os.path.abspath('preview.html')}")
        height = await page.evaluate("document.querySelector('.sheet').scrollHeight")
        await page.set_viewport_size({"width": 1280, "height": int(height) + 20})
        await page.screenshot(path="Welcome_Sign_Set_Preview_loveforlove.png", full_page=True)

        await browser.close()

    writer = PdfWriter()
    for fname in pdf_files:
        reader = PdfReader(fname)
        for pg in reader.pages:
            writer.add_page(pg)
    with open("Welcome_GuestBook_Sign_Set_loveforlove.pdf", "wb") as f:
        writer.write(f)


asyncio.run(main())
print("done")
