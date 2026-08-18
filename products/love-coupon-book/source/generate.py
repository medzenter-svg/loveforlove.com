#!/usr/bin/env python3
"""Generate the Love Coupons PDF (loveforlove.com) via HTML -> Playwright PDF."""
import asyncio
from playwright.async_api import async_playwright

COUPONS = [
    ("ROMANTIC", "Candlelit Dinner At Home", "A slow, cozy dinner just for the two of us."),
    ("ROMANTIC", "A Love Letter, Read Aloud", "Written by hand, read out loud, kept forever."),
    ("ROMANTIC", "Slow Dance In The Kitchen", "One song, no phones, just us swaying around."),
    ("ROMANTIC", "Sunset Walk Together", "Wherever the view is best, hand in hand."),
    ("PLAYFUL", "Movie Night, Your Pick", "Any movie you want, snacks included, no complaints."),
    ("PLAYFUL", "Silly Photo Booth At Home", "Funny faces, props, and a memory to keep."),
    ("PLAYFUL", "Dessert Before Dinner", "Because sometimes the rules can wait."),
    ("PLAYFUL", "A Full Day Of Your Choice", "You plan it, I follow — no questions asked."),
    ("COZY", "Breakfast In Bed", "Coffee, something sweet, and zero rushing."),
    ("COZY", "A Day Off From Chores", "I've got it covered — just relax today."),
    ("COZY", "A Massage, No Questions Asked", "Ten minutes or an hour, whenever you need it."),
    ("COZY", "Our Favorite Playlist Together", "Your songs, my full attention, nothing else."),
    ("ADVENTURE", "Mystery Day Trip", "I'll plan it, you just have to show up."),
    ("ADVENTURE", "Cook A New Recipe Together", "Something neither of us has tried before."),
    ("ADVENTURE", "Stargazing Night", "A blanket, the sky, and time to talk."),
    ("ADVENTURE", "Picnic Anywhere You Choose", "Any spot you pick, I'll bring the basket."),
]

CATEGORY_COLORS = {
    "ROMANTIC": "#b5495b",
    "PLAYFUL": "#c98a3e",
    "COZY": "#7d8f69",
    "ADVENTURE": "#5b7ea3",
}

PALETTE = {
    "bg": "#fdf7f2",
    "card": "#fffdfb",
    "border": "#d8b98f",
    "ink": "#3c2f2f",
    "muted": "#8a7a6d",
    "gold": "#c9a24b",
    "blush": "#f3ddd9",
}


def coupon_html(category, title, desc, idx):
    color = CATEGORY_COLORS[category]
    return f"""
    <div class="coupon">
      <div class="coupon-inner" style="border-color:{color}55;">
        <div class="corner tl"></div><div class="corner tr"></div>
        <div class="corner bl"></div><div class="corner br"></div>
        <div class="cat" style="color:{color};">&#10022;&nbsp; {category} &nbsp;&#10022;</div>
        <div class="title">{title}</div>
        <div class="desc">{desc}</div>
        <div class="rule"></div>
        <div class="fields">
          <span>For: ____________________</span>
          <span>From: ____________________</span>
        </div>
        <div class="footer">&hearts; Redeem any time &middot; No expiration &hearts;</div>
        <div class="num">No. {idx:02d} &middot; loveforlove.com</div>
      </div>
    </div>
    """


BRANDMARK = '<div class="brandmark">Designed by loveforlove.com</div>'


def page_of_four(items, start_idx):
    cells = "".join(
        coupon_html(cat, title, desc, start_idx + i)
        for i, (cat, title, desc) in enumerate(items)
    )
    return f'<div class="page"><div class="grid">{cells}</div>{BRANDMARK}</div>'


COVER = """
<div class="page cover">
  <div class="cover-frame">
    <div class="cover-orn">&#10084;</div>
    <div class="cover-kicker">A LOVEFORLOVE.COM ORIGINAL</div>
    <div class="cover-title">The Love<br/>Coupon Book</div>
    <div class="cover-sub">16 little promises for the person you love</div>
    <div class="cover-orn small">&#10022; &#10084; &#10022;</div>
  </div>
  <div class="brandmark">Designed by loveforlove.com</div>
</div>
"""

INSTRUCTIONS = """
<div class="page instructions">
  <div class="instr-frame">
    <div class="instr-title">How To Use This Set</div>
    <div class="instr-list">
      <div class="instr-item"><span class="num-badge">1</span>Print all pages on plain paper or cardstock — cardstock feels the most special.</div>
      <div class="instr-item"><span class="num-badge">2</span>Cut along each coupon's edge. A ruler and craft knife give the cleanest lines, but scissors work perfectly too.</div>
      <div class="instr-item"><span class="num-badge">3</span>Fill in the "For" and "From" lines by hand for a personal touch.</div>
      <div class="instr-item"><span class="num-badge">4</span>Tie the stack together with ribbon, tuck it in a card, or hide one coupon a week for a month of little surprises.</div>
      <div class="instr-item"><span class="num-badge">5</span>When a coupon is redeemed, keep it as a small memory — or let it be reused as many times as you like.</div>
    </div>
    <div class="instr-foot">Made with love for loveforlove.com &middot; Personal use only, please don't resell or redistribute this file.</div>
  </div>
  <div class="brandmark">Designed by loveforlove.com</div>
</div>
"""

STYLE = """
<style>
  @page { size: Letter; margin: 0; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: 'Poppins', sans-serif; background:#fdf7f2; }
  .page { width: 8.5in; height: 11in; position: relative; page-break-after: always; background: #fdf7f2; padding: 0.4in; }
  .page:last-child { page-break-after: auto; }

  /* Cover */
  .cover { display:flex; align-items:center; justify-content:center; background: radial-gradient(circle at 50% 30%, #fbe9e4 0%, #fdf7f2 60%); }
  .cover-frame { text-align:center; border: 1.5px solid #c9a24b88; padding: 0.9in 0.6in; width: 6.5in; }
  .cover-orn { font-size: 34px; color:#b5495b; margin-bottom: 14px; }
  .cover-orn.small { font-size: 16px; letter-spacing: 6px; margin-top: 22px; color:#c9a24b; }
  .cover-kicker { letter-spacing: 4px; font-size: 12px; color:#8a7a6d; margin-bottom: 18px; }
  .cover-title { font-family: 'Lora', serif; font-size: 56px; line-height:1.15; color:#3c2f2f; font-weight:600; }
  .cover-sub { margin-top: 18px; font-size: 16px; color:#6a5a52; font-style: italic; font-family:'Lora', serif; }

  /* Instructions */
  .instructions { display:flex; align-items:center; justify-content:center; }
  .instr-frame { width: 6.6in; }
  .instr-title { font-family:'Lora', serif; font-size: 30px; color:#3c2f2f; text-align:center; margin-bottom: 34px; }
  .instr-item { display:flex; gap: 16px; align-items:flex-start; font-size: 14px; color:#4a3d38; line-height:1.5; margin-bottom: 20px; }
  .num-badge { flex: 0 0 auto; width: 26px; height:26px; border-radius:50%; background:#b5495b; color:#fff; font-size:13px; display:flex; align-items:center; justify-content:center; font-family:'Lora',serif; }
  .instr-foot { margin-top: 40px; text-align:center; font-size: 11px; color:#9a8a7d; }

  /* Coupon grid */
  .grid { display:grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 0.2in; width: 7.7in; height: 10.2in; }
  .coupon { position:relative; }
  .coupon-inner {
    position:relative; height:100%; background:#fffdfb; border: 1.5px solid;
    border-radius: 10px; padding: 20px 22px; display:flex; flex-direction:column;
    align-items:center; text-align:center; justify-content:center;
    box-shadow: 0 0 0 1px #f0e2d0 inset;
  }
  .corner { position:absolute; width:14px; height:14px; border-color:#c9a24b; }
  .corner.tl { top:6px; left:6px; border-top:2px solid; border-left:2px solid; }
  .corner.tr { top:6px; right:6px; border-top:2px solid; border-right:2px solid; }
  .corner.bl { bottom:6px; left:6px; border-bottom:2px solid; border-left:2px solid; }
  .corner.br { bottom:6px; right:6px; border-bottom:2px solid; border-right:2px solid; }
  .cat { font-size: 11px; letter-spacing: 2px; font-weight:600; margin-bottom: 10px; }
  .title { font-family:'Lora', serif; font-size: 21px; color:#3c2f2f; font-weight:600; line-height:1.25; margin-bottom: 8px; }
  .desc { font-size: 11.5px; color:#8a7a6d; font-style: italic; font-family:'Lora',serif; margin-bottom: 14px; max-width: 90%; }
  .rule { width: 60px; height:1px; background:#d8b98f; margin-bottom: 12px; }
  .fields { display:flex; flex-direction:column; gap:6px; font-size:10.5px; color:#6a5a52; margin-bottom: 12px; }
  .footer { font-size: 10px; color:#b5495b; letter-spacing: 0.5px; margin-bottom: 6px; }
  .num { font-size: 8.5px; color:#c3b6a9; letter-spacing: 1px; }

  /* Standard brand mark, present on every page of every product */
  .brandmark { position:absolute; bottom: 0.22in; left:0; right:0; text-align:center; font-size: 8px; letter-spacing:1.5px; color:#c3b6a9; text-transform:uppercase; }
</style>
"""


def build_html():
    pages = [COVER]
    for i in range(0, len(COUPONS), 4):
        pages.append(page_of_four(COUPONS[i:i + 4], i + 1))
    pages.append(INSTRUCTIONS)
    return f"<html><head><meta charset='utf-8'>{STYLE}</head><body>{''.join(pages)}</body></html>"


async def main():
    html = build_html()
    with open("coupons.html", "w") as f:
        f.write(html)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        page = await browser.new_page()
        await page.goto(f"file://{__import__('os').path.abspath('coupons.html')}")
        await page.pdf(path="Love_Coupons_loveforlove.pdf", format="Letter", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})
        await browser.close()

asyncio.run(main())
print("done")
