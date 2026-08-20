"""Sale-ready catalog. Only products with real deliverables belong here."""

PRODUCTS = [
    {
        "slug": "love-coupon-book",
        "name": "The Love Coupon Book",
        "category": "Gifts",
        "price": 900,
        "description": "A print-ready PDF coupon book with romantic prompts for couples.",
        "cover": "love-coupon-book/cover.png",
        "files": ["Love_Coupons_loveforlove.pdf"],
    },
    {
        "slug": "save-the-date",
        "name": "Save the Date",
        "category": "Stationery",
        "price": 1200,
        "description": "An elegant, print-ready Save the Date PDF for a first announcement of your celebration.",
        "cover": "save-the-date/cover.png",
        "files": ["Save_The_Date_loveforlove.pdf"],
    },
    {
        "slug": "invitation-suite",
        "name": "Invitation Suite",
        "category": "Stationery",
        "price": 1800,
        "description": "A coordinated wedding invitation and RSVP set supplied as print-ready PDF pages.",
        "cover": "invitation-suite/cover.png",
        "files": ["Invitation_Suite_loveforlove.pdf"],
    },
    {
        "slug": "wedding-day-set",
        "name": "Wedding Day Set",
        "category": "Stationery",
        "price": 2200,
        "description": "Coordinated programs, menus and wedding-day signs in one print-ready PDF set.",
        "cover": "wedding-day-set/cover.png",
        "files": ["Wedding_Day_Set_loveforlove.pdf"],
    },
    {
        "slug": "monogram-pack",
        "name": "Monogram & Crest Pack",
        "category": "Design Elements",
        "price": 1500,
        "description": "A print-ready PDF collection of monogram and crest concepts for wedding stationery.",
        "cover": "monogram-pack/cover.png",
        "files": ["Monogram_Crest_Pack_loveforlove.pdf"],
    },
    {
        "slug": "welcome-sign-set",
        "name": "Welcome & Guest Book Sign Set",
        "category": "Ceremony",
        "price": 1600,
        "description": "Four coordinated welcome and guest-book sign designs supplied as print-ready PDF pages.",
        "cover": "welcome-sign-set/cover.png",
        "files": ["Welcome_GuestBook_Sign_Set_loveforlove.pdf"],
    },
]

PRODUCTS_BY_SLUG = {p["slug"]: p for p in PRODUCTS}


def price_display(cents):
    return f"€{cents / 100:,.2f}"
