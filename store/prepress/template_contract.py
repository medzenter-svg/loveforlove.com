PIECE_REQUIRED_FIELDS = {
    "invitation": {"coupleNames", "weddingDate", "weddingTime", "venueName", "venueAddress"},
    "venue_address": {"coupleNames", "weddingDate", "weddingTime", "venueName", "venueAddress"},
    "rsvp": {"coupleNames", "rsvpDate", "rsvpContact"},
    "menu": {"coupleNames", "course1", "course1Desc", "course2", "course2Desc", "course3", "course3Desc", "dessert", "dessertDesc"},
    "table_number": {"tableNumber", "coupleNames", "weddingDate"},
    "place_card": {"guestName", "tableNumber"},
    "program": {"coupleNames", "ceremonyTime", "cocktailsTime", "dinnerTime", "dancingTime"},
    "thank_you": {"coupleNames", "thankMessage"},
    "accommodation": {"hotelName", "hotelAddress", "hotelCheckIn", "hotelCheckOut", "hotelBooking", "hotelTransport"},
    "coordinator": {"coordinatorName", "coordinatorRole", "coordinatorPhone", "coordinatorMessenger", "coordinatorEmail"},
    "dress_code": {"dressStyle", "dressDescription", "dressNote"},
    "envelope": {"guestMailingAddress", "returnAddress"},
    "envelope_liner": {"monogram", "coupleNames"},
    "program_day_1": {"dayOneDate", "dayOneTime1", "dayOneEvent1", "dayOneTime2", "dayOneEvent2", "dayOneTime3", "dayOneEvent3", "dayOneTime4", "dayOneEvent4"},
    "program_day_2": {"dayTwoDate", "dayTwoTime1", "dayTwoEvent1", "dayTwoTime2", "dayTwoEvent2", "dayTwoTime3", "dayTwoEvent3", "dayTwoTime4", "dayTwoEvent4"},
}

PIECE_REQUIRED_LABELS = {
    "invitation": {"invitation", "join_us"},
    "venue_address": {"details", "venue", "address"},
    "rsvp": {"rsvp", "reply_by"},
    "menu": {"menu", "first", "second", "third", "dessert"},
    "table_number": {"table"},
    "place_card": {"place", "table"},
    "program": {"program", "ceremony", "cocktails", "dinner", "dancing"},
    "thank_you": {"thank_you"},
    "accommodation": {"accommodation", "check_in", "check_out", "booking", "transport"},
    "coordinator": {"guest_contact", "questions"},
    "dress_code": {"dress_code", "dress_note"},
    "envelope": {"to", "from"},
    "envelope_liner": {"envelope_liner"},
    "program_day_1": {"weekend_program", "day_one"},
    "program_day_2": {"weekend_program", "day_two"},
}


def required_frame_names(piece):
    fields = {"txt__" + key for key in PIECE_REQUIRED_FIELDS[piece]}
    labels = {"lbl__" + key for key in PIECE_REQUIRED_LABELS[piece]}
    return fields | labels
