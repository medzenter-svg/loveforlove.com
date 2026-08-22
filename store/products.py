# Product catalog for loveforlove.com
# price is in USD cents (Stripe wants the smallest currency unit)

PRODUCTS = [
    {
        "slug": "amalfi-wedding-suite",
        "name": "Amalfi Wedding Suite — 24 Piece Collection",
        "category": "Complete Wedding Collections",
        "price": 0,
        "available": False,
        "status": "FINAL QUALITY CHECK",
        "description": "A complete 24-piece Mediterranean wedding stationery suite in ivory, lemon, white blossom, greenery and gold. The collection preview is rendered from the actual print files.",
        "cover": "amalfi-wedding-suite/cover.webp",
        "files": [],
        "full_collection": True,
    },
    {
        "slug": "love-coupon-book",
        "name": "The Love Coupon Book",
        "category": "Gifts",
        "price": 900,
        "description": "A playful, printable coupon book of little promises for your favorite person — one design, endlessly personal.",
        "cover": "love-coupon-book/cover.png",
        "files": ["Love_Coupons_loveforlove.pdf"],
    },
    {
        "slug": "save-the-date",
        "name": "Save the Date",
        "category": "Stationery",
        "price": 1200,
        "description": "An elegant Save the Date card to give your guests the first glimpse of your wedding day.",
        "cover": "save-the-date/cover.png",
        "files": ["Save_The_Date_loveforlove.pdf"],
    },
    {
        "slug": "invitation-suite",
        "name": "Invitation Suite",
        "category": "Stationery",
        "price": 1800,
        "description": "A classic wedding invitation suite with a coordinating RSVP card, ready to print at home or through any printer.",
        "cover": "invitation-suite/cover.png",
        "files": ["Invitation_Suite_loveforlove.pdf"],
    },
    {
        "slug": "wedding-day-set",
        "name": "Wedding Day Set",
        "category": "Stationery",
        "price": 2200,
        "description": "Everything for the day itself — programs, menus and signage in one coordinated set.",
        "cover": "wedding-day-set/cover.png",
        "files": ["Wedding_Day_Set_loveforlove.pdf"],
    },
    {
        "slug": "monogram-pack",
        "name": "Monogram & Crest Pack",
        "category": "Designers",
        "price": 1500,
        "description": "A set of custom monogram and crest designs to carry your initials across every piece of your wedding stationery.",
        "cover": "monogram-pack/cover.png",
        "files": ["Monogram_Crest_Pack_loveforlove.pdf"],
    },
    {
        "slug": "welcome-sign-set",
        "name": "Welcome & Guest Book Sign Set",
        "category": "Ceremony",
        "price": 1600,
        "description": "Large-format welcome and guest book signs, in four coordinating styles, ready to print at 18×24in.",
        "cover": "welcome-sign-set/cover.png",
        "files": ["Welcome_GuestBook_Sign_Set_loveforlove.pdf"],
    },
    {
        "slug": "thank-you-cards",
        "name": "Thank You Cards",
        "category": "Stationery",
        "price": 1000,
        "description": "Four beautifully designed thank you card styles to send your gratitude after the big day.",
        "cover": "thank-you-cards/cover.png",
        "files": ["Thank_You_Cards_loveforlove.pdf"],
    },
    {
        "slug": "invitation-suite-floral",
        "name": "Floral Photo Invitation Suite",
        "category": "Featured Destinations",
        "price": 1900,
        "description": "A romantic invitation and RSVP card built directly on a real floral flat-lay photograph.",
        "cover": "invitation-suite-floral/cover.png",
        "files": ["Floral_Invitation_Suite_loveforlove.pdf"],
    },
    {
        "slug": "tuscany-set",
        "name": "Blush Rose Suite",
        "category": "Featured Destinations",
        "price": 2400,
        "description": "Invitation, menu and table number in a watercolor blush rose design — three matching pieces, sold as a set.",
        "cover": "tuscany-set/cover.png",
        "files": [
            "Blush_Rose_Invitation_loveforlove.pdf",
            "Blush_Rose_Menu_loveforlove.pdf",
            "Blush_Rose_Table_Number_loveforlove.pdf",
        ],
    },
    {
        "slug": "rosewood-set",
        "name": "Rosewood Garden Suite",
        "category": "Featured Destinations",
        "price": 2400,
        "description": "Invitation, menu and table number in a watercolor peony and rose design with a scalloped gold border.",
        "cover": "rosewood-set/cover.png",
        "files": [
            "Rosewood_Invitation_loveforlove.pdf",
            "Rosewood_Menu_loveforlove.pdf",
            "Rosewood_Table_Number_loveforlove.pdf",
        ],
    },
    {
        "slug": "villa-belvedere-set",
        "name": "Villa Belvedere Suite",
        "category": "Featured Destinations",
        "price": 2400,
        "description": "Invitation, menu and table number built on a photorealistic peony and rose bouquet, with a thin gold border.",
        "cover": "villa-belvedere-set/cover.png",
        "files": [
            "VillaBelvedere_Invitation_loveforlove.pdf",
            "VillaBelvedere_Menu_loveforlove.pdf",
            "VillaBelvedere_Table_Number_loveforlove.pdf",
        ],
    },
]

PRODUCTS_BY_SLUG = {p["slug"]: p for p in PRODUCTS}


def price_display(cents):
    return f"${cents / 100:,.2f}"
