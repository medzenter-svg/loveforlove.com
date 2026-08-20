"""Generate the coordinated base Scribus templates for an editable wedding suite.

Run inside Scribus Scripter:
  scribus -g -ns -py make_base_templates.py -- wedding-day-set /path/to/products

This creates 15 pieces in two independently sized families (30 SLA files).
The generated layout is the structural base. Collection-specific artwork can be
added later without changing editable frame names or professional geometry.

IMPORTANT: Before production release, each generated SLA must be opened/verified
with the approved ICC/output-intent setup. The release gate will remain closed
until the final PDF/X files pass preflight.
"""

import os
import sys

import scribus

STORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if STORE_DIR not in sys.path:
    sys.path.insert(0, STORE_DIR)

from print_piece_specs import PRINT_PIECE_SPECS
from print_package import PIECE_ORDER


TITLE_FONT = os.environ.get("LF_TITLE_FONT", "DejaVu Serif")
BODY_FONT = os.environ.get("LF_BODY_FONT", "DejaVu Sans")

COLOR_IVORY = "LF Ivory"
COLOR_BURGUNDY = "LF Burgundy"
COLOR_GOLD = "LF Gold"
COLOR_INK = "LF Ink"


DEFAULT_FIELDS = {
    "coupleNames": "Emma & James",
    "weddingDate": "14 June 2027",
    "weddingTime": "4:30 PM",
    "venueName": "Villa del Balbianello",
    "venueAddress": "Via Guido Monzino 1\n22016 Tremezzina CO, Italy",
    "rsvpDate": "15 April 2027",
    "rsvpContact": "love.example.com · hello@example.com",
    "course1": "Burrata & Heirloom Tomato",
    "course1Desc": "basil oil, aged balsamic",
    "course2": "Saffron Risotto",
    "course2Desc": "lake fish, brown butter",
    "course3": "Herb-Roasted Lamb",
    "course3Desc": "rosemary jus, seasonal vegetables",
    "dessert": "Limoncello Tart",
    "dessertDesc": "whipped mascarpone, candied lemon",
    "tableNumber": "7",
    "guestName": "Sophia Miller",
    "ceremonyTime": "4:30 PM",
    "cocktailsTime": "5:30 PM",
    "dinnerTime": "7:00 PM",
    "dancingTime": "9:00 PM",
    "thankMessage": "Thank you for celebrating this unforgettable day with us.",
    "hotelName": "Grand Hotel Tremezzo",
    "hotelAddress": "Via Regina 8\n22016 Tremezzina CO, Italy",
    "hotelCheckIn": "13 June 2027 · from 3:00 PM",
    "hotelCheckOut": "15 June 2027 · by 11:00 AM",
    "hotelBooking": "Rooms are reserved under Emma & James Wedding.",
    "hotelTransport": "Wedding shuttle departs the hotel lobby at 3:45 PM.",
    "coordinatorName": "Anna Rossi",
    "coordinatorRole": "Wedding Coordinator",
    "coordinatorPhone": "+39 333 123 4567",
    "coordinatorMessenger": "WhatsApp: +39 333 123 4567",
    "coordinatorEmail": "anna@example.com",
    "dressStyle": "White Celebration",
    "dressDescription": "We kindly invite our guests to celebrate with us in elegant white attire.",
    "dressNote": "Elegant · Festive · Summer",
    "guestMailingAddress": "Sophia Miller\n24 Garden Street\nLondon SW1A 1AA\nUnited Kingdom",
    "returnAddress": "Emma & James\n12 Lake Road\nComo 22100 · Italy",
    "monogram": "E · J",
    "dayOneDate": "13 June 2027",
    "dayOneTime1": "5:00 PM", "dayOneEvent1": "Welcome Aperitivo",
    "dayOneTime2": "7:30 PM", "dayOneEvent2": "Welcome Dinner",
    "dayOneTime3": "9:30 PM", "dayOneEvent3": "Cocktails & Music",
    "dayOneTime4": "11:30 PM", "dayOneEvent4": "Late Night",
    "dayTwoDate": "14 June 2027",
    "dayTwoTime1": "10:30 AM", "dayTwoEvent1": "Brunch",
    "dayTwoTime2": "1:00 PM", "dayTwoEvent2": "Lake Activity",
    "dayTwoTime3": "5:00 PM", "dayTwoEvent3": "Farewell Aperitivo",
    "dayTwoTime4": "7:00 PM", "dayTwoEvent4": "Farewell",
}

DEFAULT_LABELS = {
    "invitation": "Wedding Invitation", "join_us": "Together with their families, invite you to celebrate their wedding",
    "details": "Wedding Details", "venue": "Venue", "address": "Address", "rsvp": "RSVP",
    "reply_by": "Kindly reply by", "menu": "Wedding Menu", "first": "First Course",
    "second": "Second Course", "third": "Third Course", "dessert": "Dessert", "table": "Table",
    "place": "Reserved for", "program": "Wedding Program", "ceremony": "Ceremony", "cocktails": "Cocktails",
    "dinner": "Dinner", "dancing": "Dancing", "thank_you": "Thank You", "accommodation": "Guest Accommodation",
    "check_in": "Check-in", "check_out": "Check-out", "booking": "Booking Details", "transport": "Transport",
    "guest_contact": "Guest Contact", "questions": "For questions and wedding-day assistance", "phone": "Phone",
    "messenger": "WhatsApp / Messenger", "email": "Email", "dress_code": "Dress Code",
    "dress_note": "Suggested attire", "envelope": "Envelope", "to": "To", "from": "From",
    "envelope_liner": "Envelope Liner", "weekend_program": "Wedding Weekend", "day_one": "Day One", "day_two": "Day Two",
}


def _args():
    args = sys.argv[1:]
    if len(args) != 2:
        raise RuntimeError("Expected: <collection_slug> <products_root>")
    return args[0], os.path.abspath(args[1])


def _define_colors():
    scribus.defineColor(COLOR_IVORY, 0, 6, 14, 0)
    scribus.defineColor(COLOR_BURGUNDY, 25, 220, 170, 80)
    scribus.defineColor(COLOR_GOLD, 20, 60, 150, 25)
    scribus.defineColor(COLOR_INK, 0, 0, 0, 225)


def _text(name, text, x, y, w, h, size=10, color=COLOR_INK, font=BODY_FONT, align=None):
    scribus.createText(x, y, w, h, name)
    scribus.setText(text, name)
    try:
        scribus.setFont(font, name)
    except Exception:
        # Keep Scribus fallback font if the preferred font is unavailable.
        pass
    scribus.setFontSize(size, name)
    scribus.setTextColor(color, name)
    scribus.setTextDistances(0, 0, 0, 0, name)
    scribus.setTextAlignment(scribus.ALIGN_CENTERED if align is None else align, name)
    try:
        scribus.setTextVerticalAlignment(scribus.ALIGNV_CENTERED, name)
    except Exception:
        pass
    return name


def _field(key, x, y, w, h, size=10, title=False, align=None):
    return _text(
        "txt__" + key,
        DEFAULT_FIELDS.get(key, key),
        x, y, w, h,
        size=size,
        color=COLOR_INK,
        font=TITLE_FONT if title else BODY_FONT,
        align=align,
    )


def _label(key, x, y, w, h, size=7, title=False, align=None):
    return _text(
        "lbl__" + key,
        DEFAULT_LABELS.get(key, key),
        x, y, w, h,
        size=size,
        color=COLOR_BURGUNDY,
        font=TITLE_FONT if title else BODY_FONT,
        align=align,
    )


def _border(width, height, safe):
    rect = scribus.createRect(safe * 0.55, safe * 0.55, width - safe * 1.1, height - safe * 1.1, "design__gold_border")
    scribus.setFillColor("None", rect)
    scribus.setLineColor(COLOR_GOLD, rect)
    scribus.setLineWidth(0.6, rect)


def _background(width, height, bleed):
    rect = scribus.createRect(-bleed, -bleed, width + 2 * bleed, height + 2 * bleed, "design__background")
    scribus.setFillColor(COLOR_IVORY, rect)
    scribus.setLineColor(COLOR_IVORY, rect)


def _ornament(width, y, safe):
    line = scribus.createLine(width * 0.38, y, width * 0.62, y, "design__ornament")
    scribus.setLineColor(COLOR_GOLD, line)
    scribus.setLineWidth(0.5, line)


def _stacked_events(prefix, y0, width, height, safe):
    row_h = height * 0.075
    gap = height * 0.012
    time_w = width * 0.25
    event_w = width - (safe * 2) - time_w
    for idx in range(1, 5):
        y = y0 + (idx - 1) * (row_h + gap)
        _field(f"{prefix}Time{idx}", safe, y, time_w, row_h, size=8, align=scribus.ALIGN_LEFT)
        _field(f"{prefix}Event{idx}", safe + time_w, y, event_w, row_h, size=9, title=True, align=scribus.ALIGN_LEFT)


def _layout(piece, width, height, safe):
    content_w = width - 2 * safe
    x = safe

    if piece == "invitation":
        _label("invitation", x, height*.12, content_w, height*.07, 8)
        _field("coupleNames", x, height*.23, content_w, height*.16, 23, True)
        _label("join_us", x+content_w*.08, height*.40, content_w*.84, height*.10, 8, True)
        _ornament(width, height*.53, safe)
        _field("weddingDate", x, height*.57, content_w, height*.06, 9)
        _field("weddingTime", x, height*.63, content_w, height*.05, 9)
        _field("venueName", x, height*.70, content_w, height*.09, 13, True)
        _field("venueAddress", x+content_w*.08, height*.80, content_w*.84, height*.10, 7)
    elif piece == "venue_address":
        _label("details", x, height*.12, content_w, height*.08, 9)
        _field("coupleNames", x, height*.22, content_w, height*.12, 18, True)
        _ornament(width, height*.38, safe)
        _label("venue", x, height*.43, content_w, height*.05, 7)
        _field("venueName", x, height*.48, content_w, height*.10, 13, True)
        _label("address", x, height*.62, content_w, height*.05, 7)
        _field("venueAddress", x+content_w*.06, height*.67, content_w*.88, height*.12, 8)
        _field("weddingDate", x, height*.82, content_w*.5, height*.05, 8)
        _field("weddingTime", x+content_w*.5, height*.82, content_w*.5, height*.05, 8)
    elif piece == "rsvp":
        _label("rsvp", x, height*.15, content_w, height*.08, 9)
        _field("coupleNames", x, height*.27, content_w, height*.14, 17, True)
        _ornament(width, height*.47, safe)
        _label("reply_by", x, height*.53, content_w, height*.05, 7)
        _field("rsvpDate", x, height*.59, content_w, height*.08, 10, True)
        _field("rsvpContact", x+content_w*.04, height*.72, content_w*.92, height*.12, 7)
    elif piece == "menu":
        _label("menu", x, height*.08, content_w, height*.05, 8)
        _field("coupleNames", x, height*.14, content_w, height*.08, 15, True)
        courses = [("first","course1","course1Desc"),("second","course2","course2Desc"),("third","course3","course3Desc"),("dessert","dessert","dessertDesc")]
        y = height*.26
        for label_key, title_key, desc_key in courses:
            _label(label_key, x, y, content_w, height*.035, 6)
            _field(title_key, x, y+height*.035, content_w, height*.055, 9, True)
            _field(desc_key, x+content_w*.05, y+height*.085, content_w*.90, height*.045, 6)
            y += height*.155
    elif piece == "table_number":
        _label("table", x, height*.16, content_w, height*.06, 9)
        _field("tableNumber", x, height*.27, content_w, height*.32, 48, True)
        _ornament(width, height*.64, safe)
        _field("coupleNames", x, height*.69, content_w, height*.08, 12, True)
        _field("weddingDate", x, height*.79, content_w, height*.06, 8)
    elif piece == "place_card":
        _label("place", x, height*.18, content_w, height*.12, 7)
        _field("guestName", x, height*.34, content_w, height*.28, 17, True)
        _ornament(width, height*.68, safe)
        _label("table", x, height*.72, content_w*.45, height*.10, 6)
        _field("tableNumber", x+content_w*.45, height*.72, content_w*.55, height*.10, 8, True, scribus.ALIGN_LEFT)
    elif piece == "program":
        _label("program", x, height*.09, content_w, height*.06, 8)
        _field("coupleNames", x, height*.16, content_w, height*.10, 16, True)
        rows = [("ceremonyTime","ceremony"),("cocktailsTime","cocktails"),("dinnerTime","dinner"),("dancingTime","dancing")]
        y = height*.34
        for time_key, label_key in rows:
            _field(time_key, x, y, content_w*.32, height*.07, 8, align=scribus.ALIGN_LEFT)
            _label(label_key, x+content_w*.32, y, content_w*.68, height*.07, 9, True, scribus.ALIGN_LEFT)
            y += height*.12
    elif piece == "thank_you":
        _label("thank_you", x, height*.16, content_w, height*.08, 9)
        _field("coupleNames", x, height*.28, content_w, height*.16, 20, True)
        _ornament(width, height*.50, safe)
        _field("thankMessage", x+content_w*.06, height*.56, content_w*.88, height*.24, 9, True)
    elif piece == "accommodation":
        _label("accommodation", x, height*.09, content_w, height*.06, 8)
        _field("hotelName", x, height*.18, content_w, height*.10, 14, True)
        _field("hotelAddress", x+content_w*.05, height*.29, content_w*.90, height*.10, 7)
        _label("check_in", x, height*.43, content_w*.5, height*.04, 6)
        _label("check_out", x+content_w*.5, height*.43, content_w*.5, height*.04, 6)
        _field("hotelCheckIn", x, height*.48, content_w*.5, height*.09, 7)
        _field("hotelCheckOut", x+content_w*.5, height*.48, content_w*.5, height*.09, 7)
        _label("booking", x, height*.61, content_w, height*.04, 6)
        _field("hotelBooking", x+content_w*.04, height*.66, content_w*.92, height*.11, 7)
        _label("transport", x, height*.79, content_w, height*.04, 6)
        _field("hotelTransport", x+content_w*.04, height*.83, content_w*.92, height*.08, 7)
    elif piece == "coordinator":
        _label("guest_contact", x, height*.12, content_w, height*.08, 8)
        _field("coordinatorName", x, height*.25, content_w, height*.13, 16, True)
        _field("coordinatorRole", x, height*.39, content_w, height*.08, 8)
        _label("questions", x+content_w*.05, height*.49, content_w*.90, height*.09, 7, True)
        _field("coordinatorPhone", x, height*.62, content_w, height*.07, 8)
        _field("coordinatorMessenger", x, height*.70, content_w, height*.07, 7)
        _field("coordinatorEmail", x, height*.78, content_w, height*.07, 7)
    elif piece == "dress_code":
        _label("dress_code", x, height*.12, content_w, height*.07, 9)
        _field("dressStyle", x, height*.25, content_w, height*.15, 20, True)
        _ornament(width, height*.47, safe)
        _field("dressDescription", x+content_w*.08, height*.53, content_w*.84, height*.17, 9, True)
        _label("dress_note", x, height*.74, content_w, height*.05, 6)
        _field("dressNote", x, height*.80, content_w, height*.07, 8)
    elif piece == "envelope":
        _label("to", x, height*.16, content_w, height*.07, 7)
        _field("guestMailingAddress", x+content_w*.18, height*.30, content_w*.64, height*.30, 11, True)
        _label("from", x, height*.71, content_w, height*.05, 6)
        _field("returnAddress", x+content_w*.20, height*.77, content_w*.60, height*.14, 7)
    elif piece == "envelope_liner":
        _label("envelope_liner", x, height*.15, content_w, height*.07, 7)
        _field("monogram", x, height*.34, content_w, height*.24, 31, True)
        _ornament(width, height*.64, safe)
        _field("coupleNames", x, height*.69, content_w, height*.10, 11, True)
    elif piece in ("program_day_1", "program_day_2"):
        prefix = "dayOne" if piece == "program_day_1" else "dayTwo"
        label_key = "day_one" if piece == "program_day_1" else "day_two"
        _label("weekend_program", x, height*.09, content_w, height*.05, 7)
        _label(label_key, x, height*.16, content_w, height*.10, 18, True)
        _field(prefix + "Date", x, height*.27, content_w, height*.06, 8)
        _ornament(width, height*.36, safe)
        _stacked_events(prefix, height*.43, width, height, safe)
    else:
        raise RuntimeError(f"Unknown piece: {piece}")


def _unit_and_geometry(size_family, piece):
    family = PRINT_PIECE_SPECS[size_family]
    spec = family["pieces"][piece]
    if "trim_mm" in spec:
        return scribus.UNIT_MILLIMETERS, spec["trim_mm"], family["bleed_mm"], 5.0
    return scribus.UNIT_INCHES, spec["trim_in"], family["bleed_in"], 0.20


def _make_one(output_path, size_family, piece):
    unit, (width, height), bleed, safe = _unit_and_geometry(size_family, piece)
    orientation = scribus.LANDSCAPE if width > height else scribus.PORTRAIT
    base_size = (min(width, height), max(width, height))
    margins = (safe, safe, safe, safe)

    scribus.newDocument(base_size, margins, orientation, 1, unit, scribus.PAGE_1, 0, 1)
    try:
        scribus.setBleeds(bleed, bleed, bleed, bleed)
        _define_colors()
        _background(width, height, bleed)
        _border(width, height, safe)
        _layout(piece, width, height, safe)
        scribus.saveDocAs(output_path)
    finally:
        scribus.closeDoc()


def main():
    collection_slug, products_root = _args()
    for size_family in PRINT_PIECE_SPECS:
        family_dir = os.path.join(products_root, collection_slug, "prepress", size_family)
        os.makedirs(family_dir, exist_ok=True)
        for piece in PIECE_ORDER:
            output_path = os.path.join(family_dir, piece + ".sla")
            _make_one(output_path, size_family, piece)
            print(output_path)


if __name__ == "__main__":
    main()
