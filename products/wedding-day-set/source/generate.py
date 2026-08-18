#!/usr/bin/env python3
"""Generate the Wedding Day set PDF (menu + table number) for loveforlove.com via HTML -> Playwright PDF."""
import asyncio
from playwright.async_api import async_playwright

PALETTE = {
    "bg": "#F7F3ED",
    "line": "#DED4C7",
    "ink": "#181716",
    "wine": "#6F252A",
    "gold": "#B79A63",
}

BRANDMARK = '<div class="brandmark">Designed by loveforlove.com</div>'

STYLE = f"""
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:'Poppins', sans-serif; background:{PALETTE['bg']}; }}
  .page {{ position:relative; background:{PALETTE['bg']}; }}
  .menu-page {{ width:4in; height:9in; }}
  .tn-page {{ width:5in; height:7in; }}
  .frame {{ position:absolute; top:0.24in; left:0.24in; right:0.24in; bottom:0.24in;
            border:1px solid {PALETTE['gold']}; }}
  .frame-inner {{ position:absolute; top:0.32in; left:0.32in; right:0.32in; bottom:0.32in;
                  border:1px solid {PALETTE['line']}; }}

  /* Menu */
  .menu-wrap {{ position:absolute; top:0.5in; left:0.5in; right:0.5in; bottom:0.5in;
                text-align:center; display:flex; flex-direction:column; justify-content:center; }}
  .orn {{ font-size:16px; color:{PALETTE['wine']}; margin-bottom:8px; }}
  .kicker {{ font-size:10px; letter-spacing:5px; color:{PALETTE['wine']}; margin-bottom:14px; }}
  .menu-names {{ font-family:'Lora', serif; font-size:21px; font-weight:600; color:{PALETTE['ink']}; }}
  .menu-date {{ font-size:9.5px; letter-spacing:1.5px; color:#7a6f63; margin-top:6px; text-transform:uppercase; }}
  .rule {{ width:50px; height:1px; background:{PALETTE['gold']}; margin: 18px auto; }}
  .course {{ margin-bottom:20px; }}
  .course .label {{ font-size:9.5px; letter-spacing:3px; color:{PALETTE['wine']}; text-transform:uppercase; margin-bottom:6px; }}
  .course .dish {{ font-family:'Lora', serif; font-size:14px; color:{PALETTE['ink']}; font-weight:600; }}
  .course .desc {{ font-size:9.5px; color:#7a6f63; font-style:italic; font-family:'Lora',serif; margin-top:3px; }}

  /* Table number */
  .tn-wrap {{ position:absolute; inset:0; display:flex; flex-direction:column;
              align-items:center; justify-content:center; text-align:center; }}
  .tn-kicker {{ font-size:11px; letter-spacing:5px; color:{PALETTE['wine']}; margin-bottom:20px; }}
  .tn-number {{ font-family:'Lora', serif; font-size:96px; font-weight:600; color:{PALETTE['ink']}; line-height:1; }}
  .tn-rule {{ width:70px; height:1px; background:{PALETTE['gold']}; margin: 26px auto; }}
  .tn-names {{ font-family:'Lora', serif; font-style:italic; font-size:15px; color:#6a5f54; }}

  .brandmark {{ position:absolute; bottom:0.12in; left:0; right:0; text-align:center;
                font-size:7px; letter-spacing:1.5px; color:#b4a99b; text-transform:uppercase; }}
</style>
"""

MENU = f"""
<div class="page menu-page">
  <div class="frame"></div>
  <div class="frame-inner"></div>
  <div class="menu-wrap">
    <div class="orn">&#10022;</div>
    <div class="kicker">WEDDING&nbsp;MENU</div>
    <div class="menu-names">Emma &amp; James</div>
    <div class="menu-date">14 JUNE 2027 &middot; LAKE COMO</div>
    <div class="rule"></div>
    <div class="course">
      <div class="label">First</div>
      <div class="dish">Burrata &amp; Heirloom Tomato</div>
      <div class="desc">basil oil, aged balsamic</div>
    </div>
    <div class="course">
      <div class="label">Second</div>
      <div class="dish">Saffron Risotto</div>
      <div class="desc">Lake Como perch, brown butter</div>
    </div>
    <div class="course">
      <div class="label">Third</div>
      <div class="dish">Herb-Roasted Lamb</div>
      <div class="desc">rosemary jus, seasonal vegetables</div>
    </div>
    <div class="course">
      <div class="label">Dessert</div>
      <div class="dish">Limoncello Tart</div>
      <div class="desc">whipped mascarpone, candied lemon</div>
    </div>
  </div>
  {BRANDMARK}
</div>
"""

TABLE_NUMBER = f"""
<div class="page tn-page">
  <div class="frame"></div>
  <div class="frame-inner"></div>
  <div class="tn-wrap">
    <div class="tn-kicker">TABLE</div>
    <div class="tn-number">7</div>
    <div class="tn-rule"></div>
    <div class="tn-names">Emma &amp; James &middot; 14.06.2027</div>
  </div>
  {BRANDMARK}
</div>
"""


async def main():
    import os
    from pypdf import PdfWriter, PdfReader

    menu_html = f"<html><head><meta charset='utf-8'>{STYLE}</head><body>{MENU}</body></html>"
    tn_html = f"<html><head><meta charset='utf-8'>{STYLE}</head><body>{TABLE_NUMBER}</body></html>"
    with open("menu.html", "w") as f:
        f.write(menu_html)
    with open("table-number.html", "w") as f:
        f.write(tn_html)

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        page = await browser.new_page()
        await page.goto(f"file://{os.path.abspath('menu.html')}")
        await page.pdf(path="menu.pdf", width="4in", height="9in", print_background=True,
                        margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        await page.goto(f"file://{os.path.abspath('table-number.html')}")
        await page.pdf(path="table-number.pdf", width="5in", height="7in", print_background=True,
                        margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        await browser.close()

    writer = PdfWriter()
    for fname in ("menu.pdf", "table-number.pdf"):
        reader = PdfReader(fname)
        for pg in reader.pages:
            writer.add_page(pg)
    with open("Wedding_Day_Set_loveforlove.pdf", "wb") as f:
        writer.write(f)

asyncio.run(main())
print("done")
