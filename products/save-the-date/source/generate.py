#!/usr/bin/env python3
"""Generate the Save the Date card PDF (loveforlove.com) via HTML -> Playwright PDF."""
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
  @page {{ size: 5in 7in; margin: 0; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:'Poppins', sans-serif; background:{PALETTE['bg']}; }}
  .page {{ width:5in; height:7in; position:relative; background:{PALETTE['bg']};
           display:flex; align-items:center; justify-content:center; }}
  .frame {{ position:absolute; top:0.28in; left:0.28in; right:0.28in; bottom:0.28in;
            border:1px solid {PALETTE['gold']}; }}
  .frame-inner {{ position:absolute; top:0.36in; left:0.36in; right:0.36in; bottom:0.36in;
                  border:1px solid {PALETTE['line']}; }}
  .content {{ text-align:center; width:3.6in; }}
  .orn {{ font-size:20px; color:{PALETTE['wine']}; margin-bottom:14px; letter-spacing:4px; }}
  .kicker {{ font-size:12px; letter-spacing:6px; color:{PALETTE['wine']}; margin-bottom:22px; }}
  .names {{ font-family:'Lora', serif; font-size:34px; font-weight:600; color:{PALETTE['ink']};
            line-height:1.25; }}
  .amp {{ font-family:'Lora', serif; font-style:italic; font-size:22px; color:{PALETTE['gold']};
          margin: 6px 0; }}
  .rule {{ width:70px; height:1px; background:{PALETTE['gold']}; margin: 22px auto; }}
  .date {{ font-family:'Lora', serif; font-size:19px; color:{PALETTE['ink']}; letter-spacing:1px; }}
  .place {{ font-size:11px; letter-spacing:2px; color:#7a6f63; margin-top:8px; text-transform:uppercase; }}
  .foot {{ margin-top:28px; font-size:10px; letter-spacing:2px; color:{PALETTE['gold']};
           text-transform:uppercase; }}
  .brandmark {{ position:absolute; bottom:0.14in; left:0; right:0; text-align:center;
                font-size:7.5px; letter-spacing:1.5px; color:#b4a99b; text-transform:uppercase; }}
</style>
"""

PAGE = """
<div class="page">
  <div class="frame"></div>
  <div class="frame-inner"></div>
  <div class="content">
    <div class="orn">&#10022;</div>
    <div class="kicker">SAVE&nbsp;THE&nbsp;DATE</div>
    <div class="names">Emma<br/>&amp; James</div>
    <div class="rule"></div>
    <div class="date">The Fourteenth of June, Twenty Twenty-Seven</div>
    <div class="place">LAKE COMO &middot; ITALY</div>
    <div class="foot">Formal invitation to follow</div>
  </div>
  BRANDMARK
</div>
""".replace("BRANDMARK", BRANDMARK)


async def main():
    html = f"<html><head><meta charset='utf-8'>{STYLE}</head><body>{PAGE}</body></html>"
    with open("save-the-date.html", "w") as f:
        f.write(html)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        page = await browser.new_page()
        await page.goto(f"file://{__import__('os').path.abspath('save-the-date.html')}")
        await page.pdf(path="Save_The_Date_loveforlove.pdf", width="5in", height="7in",
                        print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        await browser.close()

asyncio.run(main())
print("done")
