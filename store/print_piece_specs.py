PRINT_PIECE_SPECS = {
    "international_metric": {
        "name": "International Metric",
        "bleed_mm": 3,
        "pieces": {
            "invitation": {"trim_mm": [105, 148], "standard": "A6"},
            "venue_address": {"trim_mm": [105, 148], "standard": "A6"},
            "rsvp": {"trim_mm": [74, 105], "standard": "A7"},
            "menu": {"trim_mm": [99, 210], "standard": "DL"},
            "table_number": {"trim_mm": [105, 148], "standard": "A6"},
            "place_card": {"trim_mm": [85, 55], "standard": "EU business-card proportion"},
            "program": {"trim_mm": [148, 210], "standard": "A5"},
            "thank_you": {"trim_mm": [105, 148], "standard": "A6"},
            "accommodation": {"trim_mm": [105, 148], "standard": "A6"},
            "coordinator": {"trim_mm": [74, 105], "standard": "A7"},
            "dress_code": {"trim_mm": [105, 148], "standard": "A6"},
            "envelope": {"trim_mm": [162, 114], "standard": "C6"},
            "envelope_liner": {"trim_mm": [162, 114], "standard": "C6 liner template"},
            "program_day_1": {"trim_mm": [105, 148], "standard": "A6"},
            "program_day_2": {"trim_mm": [105, 148], "standard": "A6"},
        },
    },
    "north_america": {
        "name": "North America",
        "bleed_in": 0.125,
        "pieces": {
            "invitation": {"trim_in": [5.0, 7.0], "standard": "5 x 7 in"},
            "venue_address": {"trim_in": [4.0, 6.0], "standard": "4 x 6 in"},
            "rsvp": {"trim_in": [3.5, 5.0], "standard": "3.5 x 5 in"},
            "menu": {"trim_in": [4.0, 9.0], "standard": "4 x 9 in"},
            "table_number": {"trim_in": [5.0, 7.0], "standard": "5 x 7 in"},
            "place_card": {"trim_in": [3.5, 2.0], "standard": "3.5 x 2 in"},
            "program": {"trim_in": [5.0, 7.0], "standard": "5 x 7 in"},
            "thank_you": {"trim_in": [5.0, 3.5], "standard": "5 x 3.5 in"},
            "accommodation": {"trim_in": [5.0, 7.0], "standard": "5 x 7 in"},
            "coordinator": {"trim_in": [5.0, 3.5], "standard": "5 x 3.5 in"},
            "dress_code": {"trim_in": [5.0, 7.0], "standard": "5 x 7 in"},
            "envelope": {"trim_in": [7.25, 5.25], "standard": "A7 envelope"},
            "envelope_liner": {"trim_in": [7.25, 5.25], "standard": "A7 envelope liner template"},
            "program_day_1": {"trim_in": [5.0, 7.0], "standard": "5 x 7 in"},
            "program_day_2": {"trim_in": [5.0, 7.0], "standard": "5 x 7 in"},
        },
    },
}

# Each piece is exported separately in both size families. The design language stays
# identical, while typography and spacing may reflow slightly to respect the different
# aspect ratios and safe areas. Never scale one final PDF blindly into the other size.
