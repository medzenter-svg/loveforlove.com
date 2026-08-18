#!/usr/bin/env python3
"""Generate the Wedding Invitation Suite PDF (loveforlove.com) via HTML -> Playwright PDF."""
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
           display:flex; align-items:center; justify-content:center; page-break-after: always; }}
  .page:last-child {{ page-break-after: auto; }}
  .frame {{ position:absolute; top:0.28in; left:0.28in; right:0.28in; bottom:0.28in;
            border:1px solid {PALETTE['gold']}; }}
  .frame-inner {{ position:absolute; top:0.36in; left:0.36in; right:0.36in; bottom:0.36in;
                  border:1px solid {PALETTE['line']}; }}
  .content {{ text-align:center; width:3.7in; }}
  .orn {{ font-size:20px; color:{PALETTE['wine']}; margin-bottom:12px; letter-spacing:4px; }}
  .kicker {{ font-size:11px; letter-spacing:5px; color:{PALETTE['wine']}; margin-bottom:18px; }}
  .names {{ font-family:'Lora', serif; font-size:32px; font-weight:600; color:{PALETTE['ink']};
            line-height:1.25; }}
  .invite-line {{ font-size:11.5px; color:#6a5f54; margin: 16px 0 6px; font-style:italic;
                   font-family:'Lora', serif; }}
  .rule {{ width:60px; height:1px; background:{PALETTE['gold']}; margin: 16px auto; }}
  .date {{ font-family:'Lora', serif; font-size:17px; color:{PALETTE['ink']}; letter-spacing:0.5px; }}
  .time {{ font-size:11px; color:#6a5f54; margin-top:6px; }}
  .place {{ font-size:12px; color:{PALETTE['ink']}; margin-top:14px; line-height:1.5; }}
  .place b {{ font-family:'Lora', serif; font-weight:600; }}
  .foot {{ margin-top:22px; font-size:10px; letter-spacing:2px; color:{PALETTE['gold']};
           text-transform:uppercase; }}
  .brandmark {{ position:absolute; bottom:0.14in; left:0; right:0; text-align:center;
                font-size:7.5px; letter-spacing:1.5px; color:#b4a99b; text-transform:uppercase; }}

  /* RSVP specific */
  .rsvp-title {{ font-family:'Lora', serif; font-size:24px; color:{PALETTE['ink']}; letter-spacing:2px; margin-bottom:26px; }}
  .field {{ text-align:left; width:3.3in; margin: 0 auto 20px; }}
  .field .label {{ font-size:10px; letter-spacing:2px; color:{PALETTE['wine']}; text-transform:uppercase; margin-bottom:6px; }}
  .field .fill {{ border-bottom:1px solid {PALETTE['line']}; height:22px; }}
  .options {{ text-align:left; width:3.3in; margin: 0 auto; font-size:12px; color:{PALETTE['ink']}; line-height:2.1; }}
  .options .box {{ display:inline-block; width:11px; height:11px; border:1px solid {PALETTE['gold']}; margin-right:10px; vertical-align:middle; }}
  .rsvp-foot {{ margin-top:26px; font-size:10px; color:#7a6f63; font-style:italic; font-family:'Lora',serif; }}
</style>
"""

INVITATION = f"""
<div class="page">
  <div class="frame"></div>
  <div class="frame-inner"></div>
  <div class="content">
    <div class="orn">&#10022;</div>
    <div class="kicker">TOGETHER&nbsp;WITH&nbsp;THEIR&nbsp;FAMILIES</div>
    <div class="names">Emma<br/>&amp; James</div>
    <div class="invite-line">request the pleasure of your company<br/>at the celebration of their marriage</div>
    <div class="rule"></div>
    <div class="date">Saturday, the Fourteenth of June<br/>Twenty Twenty-Seven</div>
    <div class="time">Half Past Four in the Afternoon</div>
    <div class="place"><b>Villa Cimbrone</b><br/>Lake Como, Italy</div>
    <div class="foot">Reception to follow</div>
  </div>
  {BRANDMARK}
</div>
"""

RSVP = f"""
<div class="page">
  <div class="frame"></div>
  <div class="frame-inner"></div>
  <div class="content">
    <div class="rsvp-title">RSVP</div>
    <div class="field">
      <div class="label">Name</div>
      <div class="fill"></div>
    </div>
    <div class="options">
      <div><span class="box"></span>Joyfully accepts</div>
      <div><span class="box"></span>Regretfully declines</div>
    </div>
    <div class="field" style="margin-top:22px;">
      <div class="label">Number of Guests</div>
      <div class="fill"></div>
    </div>
    <div class="field">
      <div class="label">Dietary Restrictions</div>
      <div class="fill"></div>
    </div>
    <div class="rsvp-foot">Kindly reply by the first of May</div>
  </div>
  {BRANDMARK}
</div>
"""


async def main():
    html = f"<html><head><meta charset='utf-8'>{STYLE}</head><body>{INVITATION}{RSVP}</body></html>"
    with open("invitation-suite.html", "w") as f:
        f.write(html)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        page = await browser.new_page()
        await page.goto(f"file://{__import__('os').path.abspath('invitation-suite.html')}")
        await page.pdf(path="Invitation_Suite_loveforlove.pdf", width="5in", height="7in",
                        print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        await browser.close()

asyncio.run(main())
print("done")
