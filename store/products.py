# Product catalog for loveforlove.com
# price is in USD cents (Stripe wants the smallest currency unit)

OCCASION_ROADMAP = [
    {"name": "Weddings", "status": "building", "note": "Complete coordinated wedding suites and wedding-day stationery are being rebuilt to professional worldwide print standards."},
    {"name": "Wedding Anniversaries & Vow Renewals", "status": "building", "note": "Milestone anniversaries, renewal ceremonies and celebration dinners."},
    {"name": "Milestone Birthdays", "status": "building", "note": "Premium adult celebrations including 18, 21, 30, 40, 50, 60, 70 and 80+."},
    {"name": "Engagement & Bridal Events", "status": "building", "note": "Engagement parties, bridal showers, rehearsal dinners and related events."},
    {"name": "Family Celebrations", "status": "planned", "note": "Baby showers, christenings and selected elegant family occasions."},
]

FULL_SUITE_ITEMS = [
    "Invitation",
    "Venue & Address Card",
    "RSVP Card",
    "Four-Course Menu",
    "Table Number",
    "Guest Place Card",
    "Wedding Program",
    "Thank You Card",
    "Guest Accommodation / Hotel Card (optional)",
    "Wedding Coordinator Contact Card (optional)",
    "Dress Code Card (optional)",
    "Matching Envelope Design (optional)",
    "Matching Envelope Liner (optional)",
    "Wedding Weekend Program — Day 1 (optional)",
    "Wedding Weekend Program — Day 2 (optional)",
]

PRO_PRINT_SPEC = {
    "resolution": "300 DPI minimum for raster artwork at final size",
    "bleed_eu": "3 mm on every edge",
    "bleed_us": "0.125 in on every edge",
    "safe_area": "Keep critical text at least 5 mm / 0.2 in inside trim",
    "primary_pdf": "PDF/X-4 professional master",
    "compatibility_pdf": "PDF/X-1a compatibility master",
    "color": "ICC color-managed production PDF with output intent",
    "fonts": "Embed fonts or convert selected display lettering to outlines",
    "delivery": "Each printed piece exported as its own professional file in metric and North American size families",
}

PRODUCTS = [
    {
        "slug": "love-coupon-book",
        "name": "The Love Coupon Book",
        "category": "Gifts",
        "occasion": "Love & Anniversary",
        "price": 900,
        "description": "A playful, printable coupon book of little promises for your favorite person — one design, endlessly personal.",
        "cover": "love-coupon-book/cover.png",
        "files": ["Love_Coupons_loveforlove.pdf"],
    },
    {
        "slug": "save-the-date",
        "name": "Save the Date",
        "category": "Stationery",
        "occasion": "Weddings",
        "price": 1200,
        "description": "An elegant Save the Date card to give your guests the first glimpse of your wedding day.",
        "cover": "save-the-date/cover.png",
        "files": ["Save_The_Date_loveforlove.pdf"],
    },
    {
        "slug": "invitation-suite",
        "name": "Invitation Suite",
        "category": "Stationery",
        "occasion": "Weddings",
        "price": 1800,
        "description": "A classic wedding invitation suite with a coordinating RSVP card.",
        "cover": "invitation-suite/cover.png",
        "files": ["Invitation_Suite_loveforlove.pdf"],
    },
    {
        "slug": "wedding-day-set",
        "name": "Editable Complete Wedding Suite",
        "category": "Stationery",
        "occasion": "Weddings",
        "price": 2200,
        "description": "A coordinated premium wedding system with eight core pieces plus seven optional guest and weekend pieces: hotel, coordinator, Dress Code, envelope, liner, Day 1 program and Day 2 program. Personalize all wording while the visual identity remains consistent.",
        "cover": "wedding-day-set/cover.png",
        "files": ["Wedding_Day_Set_loveforlove.pdf"],
        "editable": True,
        "custom_language": True,
        "language_presets": ["en", "de", "fr", "it", "es", "pt", "nl", "pl", "el", "ru", "tr"],
        "suite_items": FULL_SUITE_ITEMS,
        "print_spec": PRO_PRINT_SPEC,
        "professional_print_package_ready": False,
        "published": False,
        "suite_theme": {
            "bg": "#F7F3ED",
            "paper": "#FFFDF9",
            "ink": "#181716",
            "accent": "#6F252A",
            "gold": "#B79A63",
            "line": "#DED4C7",
        },
    },
    {
        "slug": "monogram-pack",
        "name": "Monogram & Crest Pack",
        "category": "Designers",
        "occasion": "Weddings",
        "price": 1500,
        "description": "A set of custom monogram and crest designs to carry your initials across every piece of your wedding stationery.",
        "cover": "monogram-pack/cover.png",
        "files": ["Monogram_Crest_Pack_loveforlove.pdf"],
    },
    {
        "slug": "welcome-sign-set",
        "name": "Welcome & Guest Book Sign Set",
        "category": "Ceremony",
        "occasion": "Weddings",
        "price": 1600,
        "description": "Large-format welcome and guest book signs in coordinating styles.",
        "cover": "welcome-sign-set/cover.png",
        "files": ["Welcome_GuestBook_Sign_Set_loveforlove.pdf"],
    },
    {
        "slug": "thank-you-cards",
        "name": "Thank You Cards",
        "category": "Stationery",
        "occasion": "Weddings",
        "price": 1000,
        "description": "Four beautifully designed thank you card styles to send your gratitude after the big day.",
        "cover": "thank-you-cards/cover.png",
        "files": ["Thank_You_Cards_loveforlove.pdf"],
        "published": False,
    },
    {
        "slug": "invitation-suite-floral",
        "name": "Floral Photo Invitation Suite",
        "category": "Featured Destinations",
        "occasion": "Weddings",
        "price": 1900,
        "description": "A romantic invitation and RSVP card built directly on a real floral flat-lay photograph.",
        "cover": "invitation-suite-floral/cover.png",
        "files": ["Floral_Invitation_Suite_loveforlove.pdf"],
        "published": False,
    },
    {
        "slug": "tuscany-set",
        "name": "Blush Rose Suite",
        "category": "Featured Destinations",
        "occasion": "Weddings",
        "price": 2400,
        "description": "Invitation, menu and table number in a watercolor blush rose design — three matching pieces, sold as a set.",
        "cover": "tuscany-set/cover.png",
        "files": ["Blush_Rose_Invitation_loveforlove.pdf", "Blush_Rose_Menu_loveforlove.pdf", "Blush_Rose_Table_Number_loveforlove.pdf"],
        "published": False,
    },
    {
        "slug": "rosewood-set",
        "name": "Rosewood Garden Suite",
        "category": "Featured Destinations",
        "occasion": "Weddings",
        "price": 2400,
        "description": "Invitation, menu and table number in a watercolor peony and rose design with a scalloped gold border.",
        "cover": "rosewood-set/cover.png",
        "files": ["Rosewood_Invitation_loveforlove.pdf", "Rosewood_Menu_loveforlove.pdf", "Rosewood_Table_Number_loveforlove.pdf"],
        "published": False,
    },
    {
        "slug": "villa-belvedere-set",
        "name": "Villa Belvedere Suite",
        "category": "Featured Destinations",
        "occasion": "Weddings",
        "price": 2400,
        "description": "Invitation, menu and table number built on a photorealistic peony and rose bouquet, with a thin gold border.",
        "cover": "villa-belvedere-set/cover.png",
        "files": ["VillaBelvedere_Invitation_loveforlove.pdf", "VillaBelvedere_Menu_loveforlove.pdf", "VillaBelvedere_Table_Number_loveforlove.pdf"],
        "published": False,
    },
]


def is_sellable_product(product):
    if not product.get("published", True):
        return False
    # Every wedding print product is now held to the same professional prepress gate.
    if product.get("occasion") == "Weddings" and not product.get("professional_print_package_ready", False):
        return False
    if product.get("editable") and not product.get("professional_print_package_ready", False):
        return False
    return True


PUBLISHED_PRODUCTS = [p for p in PRODUCTS if is_sellable_product(p)]
PRODUCTS_BY_SLUG = {p["slug"]: p for p in PRODUCTS}


def price_display(cents):
    return f"${cents / 100:,.2f}"
