"""Единый источник истины для 24 утвержденных элементов свадебной полиграфии.

Графический дизайн коллекции здесь не хранится: коллекции меняют только CSS, фон,
цвета и шрифты. Размеры, стороны, поля и языковая структура фиксированы здесь.
"""

SUPPORTED_LANGUAGES = ("en", "de", "fr", "it", "es", "ru")
DEFAULT_BLEED_MM = 3
EXPECTED_CARD_COUNT = 24

COMMON = {
    "en": {"names": "Olivia & Matteo", "date": "June 12, 2027", "location": "Ravello, Amalfi Coast, Italy", "greeting": "We would be delighted to celebrate with you."},
    "de": {"names": "Olivia & Matteo", "date": "12. Juni 2027", "location": "Ravello, Amalfiküste, Italien", "greeting": "Wir freuen uns, diesen besonderen Tag mit euch zu feiern."},
    "fr": {"names": "Olivia & Matteo", "date": "12 juin 2027", "location": "Ravello, Côte amalfitaine, Italie", "greeting": "Nous serions heureux de célébrer cette journée avec vous."},
    "it": {"names": "Olivia & Matteo", "date": "12 giugno 2027", "location": "Ravello, Costiera Amalfitana, Italia", "greeting": "Saremmo felici di celebrare questo giorno con voi."},
    "es": {"names": "Olivia & Matteo", "date": "12 de junio de 2027", "location": "Ravello, Costa Amalfitana, Italia", "greeting": "Nos encantará celebrar este día con vosotros."},
    "ru": {"names": "Оливия и Маттео", "date": "12 июня 2027", "location": "Равелло, Амальфитанское побережье, Италия", "greeting": "Будем рады разделить с вами этот особенный день."},
}


def translations(titles, extras=None):
    extras = extras or {}
    result = {}
    for lang in SUPPORTED_LANGUAGES:
        payload = dict(COMMON[lang])
        payload["title"] = titles[lang]
        payload.update(extras.get(lang, {}))
        result[lang] = payload
    return result


def item(card_id, number, name, w_mm, h_mm, titles, *, views=("front",), orientation="landscape", fields=None, extras=None, fold=False, finished=None):
    data = {
        "id": card_id,
        "number": number,
        "name": name,
        "w_mm": w_mm,
        "h_mm": h_mm,
        "bleed_mm": DEFAULT_BLEED_MM,
        "orientation": orientation,
        "views": list(views),
        "fields": fields or ["title", "names", "date", "location", "greeting"],
        "translations": translations(titles, extras),
        "fold": fold,
    }
    if finished:
        data["finished_w_mm"], data["finished_h_mm"] = finished
    return data


T = {
    "save": {"en":"Save the Date","de":"Save the Date","fr":"Réservez la date","it":"Save the Date","es":"Reserva la fecha","ru":"Сохраните дату"},
    "invitation": {"en":"Wedding Invitation","de":"Hochzeitseinladung","fr":"Invitation de mariage","it":"Invito di matrimonio","es":"Invitación de boda","ru":"Приглашение на свадьбу"},
    "details": {"en":"Wedding Details","de":"Hochzeitsdetails","fr":"Informations","it":"Dettagli","es":"Detalles","ru":"Детали свадьбы"},
    "rsvp": {"en":"Kindly Reply","de":"Bitte um Antwort","fr":"Merci de répondre","it":"Gentile conferma","es":"Confirmación","ru":"Подтвердите участие"},
    "website": {"en":"Wedding Website","de":"Hochzeitswebsite","fr":"Site du mariage","it":"Sito del matrimonio","es":"Web de la boda","ru":"Сайт свадьбы"},
    "hotel": {"en":"Accommodation","de":"Unterkunft","fr":"Hébergement","it":"Alloggio","es":"Alojamiento","ru":"Проживание"},
    "transport": {"en":"Transport & Parking","de":"Transport & Parken","fr":"Transport & Parking","it":"Trasporto & Parcheggio","es":"Transporte y Aparcamiento","ru":"Трансфер и парковка"},
    "dress": {"en":"Dress Code","de":"Dresscode","fr":"Code vestimentaire","it":"Dress Code","es":"Código de vestimenta","ru":"Дресс-код"},
    "gifts": {"en":"Gifts & Registry","de":"Geschenke","fr":"Cadeaux","it":"Regali","es":"Regalos","ru":"Подарки"},
    "coordinator": {"en":"Wedding Coordinator","de":"Hochzeitskoordination","fr":"Coordinateur du mariage","it":"Wedding Coordinator","es":"Coordinador de la boda","ru":"Координатор свадьбы"},
    "general": {"en":"Wedding Weekend Program","de":"Hochzeitswochenende","fr":"Programme du week-end","it":"Programma del weekend","es":"Programa del fin de semana","ru":"Программа свадебного уикенда"},
    "day1": {"en":"Day One Program","de":"Programm Tag Eins","fr":"Programme Jour Un","it":"Programma Giorno Uno","es":"Programa Día Uno","ru":"Программа первого дня"},
    "day2": {"en":"Day Two Program","de":"Programm Tag Zwei","fr":"Programme Jour Deux","it":"Programma Giorno Due","es":"Programa Día Dos","ru":"Программа второго дня"},
    "program": {"en":"Wedding Program","de":"Hochzeitsprogramm","fr":"Programme du mariage","it":"Programma del matrimonio","es":"Programa de boda","ru":"Программа свадьбы"},
    "ceremony": {"en":"Ceremony","de":"Trauung","fr":"Cérémonie","it":"Cerimonia","es":"Ceremonia","ru":"Церемония"},
    "order": {"en":"Order of Ceremony","de":"Ablauf der Zeremonie","fr":"Déroulement de la cérémonie","it":"Ordine della cerimonia","es":"Orden de la ceremonia","ru":"Порядок церемонии"},
    "reception": {"en":"Reception","de":"Empfang","fr":"Réception","it":"Ricevimento","es":"Recepción","ru":"Приём"},
    "menu": {"en":"Menu","de":"Menü","fr":"Menu","it":"Menu","es":"Menú","ru":"Меню"},
    "table": {"en":"Table","de":"Tisch","fr":"Table","it":"Tavolo","es":"Mesa","ru":"Стол"},
    "place": {"en":"Place Card","de":"Platzkarte","fr":"Marque-place","it":"Segnaposto","es":"Tarjeta de sitio","ru":"Карточка гостя"},
    "welcome": {"en":"Welcome","de":"Willkommen","fr":"Bienvenue","it":"Benvenuti","es":"Bienvenidos","ru":"Добро пожаловать"},
    "guestbook": {"en":"Guest Book","de":"Gästebuch","fr":"Livre d'or","it":"Libro degli ospiti","es":"Libro de invitados","ru":"Книга пожеланий"},
    "thanks": {"en":"Thank You","de":"Danke","fr":"Merci","it":"Grazie","es":"Gracias","ru":"Спасибо"},
    "envelope": {"en":"Envelope Suite","de":"Umschlag-Set","fr":"Suite d'enveloppes","it":"Set buste","es":"Set de sobres","ru":"Комплект конверта"},
}

WEBSITE_COPY = {
    "en": {"info": "For travel, schedule, and updates, please visit", "password_label": "Password:"},
    "de": {"info": "Reiseinformationen, Programm und Neuigkeiten finden Sie unter", "password_label": "Passwort:"},
    "fr": {"info": "Pour le voyage, le programme et les actualités, rendez-vous sur", "password_label": "Mot de passe :"},
    "it": {"info": "Per viaggio, programma e aggiornamenti, visitate", "password_label": "Password:"},
    "es": {"info": "Para viaje, programa y novedades, visite", "password_label": "Contraseña:"},
    "ru": {"info": "Вся информация о поездке, программе и обновлениях — на сайте", "password_label": "Пароль:"},
}

CARDS_CONFIG = [
    item("01_save_the_date",1,"Save the Date",175,125,T["save"],views=("option_a","option_b"),fields=["title","names","date","venue","location","greeting"],extras={l:{"venue":"Villa Cimbrone"} for l in SUPPORTED_LANGUAGES}),
    item("02_main_invitation",2,"Main Invitation",180,130,T["invitation"],views=("front","back"),fields=["title","greeting","names","date","time","venue","location","reception","dress_code"],extras={l:{"time":"3:30 PM" if l=="en" else "15:30","venue":"Villa Cimbrone","reception":"Reception to follow","dress_code":"Mediterranean Formal"} for l in SUPPORTED_LANGUAGES}),
    item("03_details_card",3,"Details Card",165,115,T["details"],views=("front","back"),fields=["title","ceremony_time","ceremony_venue","reception_time","reception_venue","dress_code","accommodation","transport","dietary"],extras={l:{"ceremony_time":"15:30","ceremony_venue":"Villa Cimbrone","reception_time":"18:30","reception_venue":"Villa Cimbrone Terrace","dress_code":"Mediterranean Formal","accommodation":"Hotel Santa Caterina","transport":"Guest shuttle","dietary":"Please add dietary requirements"} for l in SUPPORTED_LANGUAGES}),
    item("04_rsvp",4,"RSVP Card",140,95,T["rsvp"],views=("front","back"),fields=["title","deadline","guest_name","accept","decline","guest_count","meal","thanks"],extras={l:{"deadline":"15 April 2027","guest_name":"Guest name","accept":"Accepts with pleasure","decline":"Declines with regret","guest_count":"2","meal":"Sea bass / Beef / Vegetarian","thanks":"Thank you for your reply"} for l in SUPPORTED_LANGUAGES}),
    item("05_wedding_website",5,"Wedding Website Card",125,85,T["website"],fields=["names","website","password"],extras={l:{"info":WEBSITE_COPY[l]["info"],"password_label":WEBSITE_COPY[l]["password_label"],"website":"loveforlove.com/olivia-matteo","password":"forever"} for l in SUPPORTED_LANGUAGES}),
    item("06_hotel_accommodation",6,"Hotel Accommodation Card",170,110,T["hotel"],fields=["title","hotel","address","stay_dates","check_in","check_out","rate","booking_code","contact","transfer","payment_note"],extras={l:{"hotel":"Hotel Santa Caterina","address":"S.S. Amalfitana 9, Amalfi, Italy","stay_dates":"11–13 June 2027","check_in":"15:00","check_out":"11:00","rate":"Wedding rate","booking_code":"LOVE2027","contact":"+39 089 871012","transfer":"Wedding-day shuttle included","payment_note":"The couple covers one night; guests pay additional nights and extras."} for l in SUPPORTED_LANGUAGES}),
    item("07_transport_parking",7,"Transport & Parking Card",160,105,T["transport"],fields=["title","departure","departure_time","return_transfer","parking","parking_address","instructions"],extras={l:{"departure":"Hotel Santa Caterina","departure_time":"14:45","return_transfer":"00:30","parking":"Parcheggio Luna Rossa","parking_address":"Via Pantaleone Comite 33, Amalfi","instructions":"Please arrive 15 minutes early."} for l in SUPPORTED_LANGUAGES}),
    item("08_dress_code",8,"Dress Code Card",210,140,T["dress"],fields=["title","day_one_style","day_one_palette","day_one_recommendations","day_two_style","day_two_palette","day_two_recommendations"],extras={l:{"day_one_style":"Garden Cocktail","day_one_palette":"Lemon · Sage · Ivory · Gold","day_one_recommendations":"Elegant summer attire","day_two_style":"Formal Elegant","day_two_palette":"Ivory · Sage · Gold","day_two_recommendations":"Formal garden attire"} for l in SUPPORTED_LANGUAGES}),
    item("09_gifts_registry",9,"Gifts & Registry Card",155,105,T["gifts"],fields=["title","greeting","registry"],extras={l:{"registry":"loveforlove.com/registry"} for l in SUPPORTED_LANGUAGES}),
    item("10_coordinator_contacts",10,"Coordinator Contacts Card",135,90,T["coordinator"],fields=["title","name","role","phone","email","second_contact"],extras={l:{"name":"Sofia Bellini","role":"Guest Relations & Wedding Coordinator","phone":"+39 333 555 0198","email":"sofia@bellinievents.it","second_contact":"Luca Romano · +39 333 555 0201"} for l in SUPPORTED_LANGUAGES}),
    item("11_general_program",11,"General Program",220,145,T["general"],fields=["title","date","event_1","event_2","event_3","event_4"],extras={l:{"event_1":"Friday · Welcome Dinner · 19:00","event_2":"Saturday · Ceremony · 15:30","event_3":"Saturday · Reception · 18:30","event_4":"Sunday · Farewell Brunch · 11:00"} for l in SUPPORTED_LANGUAGES}),
    item("12_day_one_program",12,"Day One Program",215,140,T["day1"],fields=["title","date","event_1","event_2","event_3"],extras={l:{"date":"11 June 2027","event_1":"16:00 · Guest arrival & check-in","event_2":"19:00 · Welcome dinner","event_3":"21:30 · Sunset cocktails"} for l in SUPPORTED_LANGUAGES}),
    item("13_day_two_program",13,"Day Two Program",205,135,T["day2"],fields=["title","date","event_1","event_2","event_3","event_4"],extras={l:{"date":"12 June 2027","event_1":"15:30 · Ceremony","event_2":"18:30 · Reception","event_3":"20:00 · Dinner","event_4":"22:00 · Dancing"} for l in SUPPORTED_LANGUAGES}),
    item("14_wedding_program",14,"Wedding Program Card",225,150,T["program"],views=("front","back"),fields=["title","day_one_program","day_two_program"],extras={l:{"day_one_program":"Welcome Dinner · 11 June 2027","day_two_program":"Wedding Day · 12 June 2027"} for l in SUPPORTED_LANGUAGES}),
    item("15_ceremony",15,"Ceremony Card",165,100,T["ceremony"],fields=["title","date","time","venue","location","greeting"],extras={l:{"time":"15:30","venue":"Belvedere Chapel"} for l in SUPPORTED_LANGUAGES}),
    item("16_order_of_ceremony",16,"Order of Ceremony",230,150,T["order"],fields=["title","processional","reading","vows","rings","unity","presentation","recessional"],extras={l:{"processional":"Processional","reading":"Reading","vows":"Exchange of Vows","rings":"Exchange of Rings","unity":"Unity Ceremony","presentation":"Presentation","recessional":"Recessional"} for l in SUPPORTED_LANGUAGES}),
    item("17_reception",17,"Reception Card",150,100,T["reception"],fields=["title","time","venue","location","greeting"],extras={l:{"time":"18:30","venue":"Villa Cimbrone Terrace"} for l in SUPPORTED_LANGUAGES}),
    item("18_menu",18,"Menu Card",140,210,T["menu"],orientation="portrait",fields=["title","starter","first_course","main_course","dessert","drinks"],extras={l:{"starter":"Burrata · Amalfi lemon · basil","first_course":"Handmade ravioli","main_course":"Sea bass · seasonal vegetables","dessert":"Lemon delight","drinks":"Italian wine · water · coffee"} for l in SUPPORTED_LANGUAGES}),
    item("19_table_number",19,"Table Number",120,240,T["table"],orientation="portrait",fold=True,finished=(120,120),views=("open",),fields=["title","table_number"],extras={l:{"table_number":"08"} for l in SUPPORTED_LANGUAGES}),
    item("20_place_card",20,"Place Card",120,140,T["place"],orientation="portrait",fold=True,finished=(120,70),views=("open",),fields=["title","guest_name"],extras={l:{"guest_name":"Sophia Rossi"} for l in SUPPORTED_LANGUAGES}),
    item("21_welcome_sign",21,"Welcome Sign",700,500,T["welcome"],fields=["title","greeting","names","date"]),
    item("22_guest_book_sign",22,"Guest Book Sign",250,200,T["guestbook"],fields=["title","greeting"]),
    item("23_thank_you",23,"Thank You Card",145,90,T["thanks"],views=("front","back"),fields=["title","greeting","names"]),
    item("24_envelope_suite",24,"Envelope Suite",225,345,T["envelope"],orientation="portrait",views=("front","back","flap","liner"),fold=True,finished=(195,145),fields=["recipient_name","recipient_address","return_names","return_address","flap_note","liner_text"],extras={l:{"recipient_name":"Sophia Rossi","recipient_address":"22 Via Roma · Milano · Italy","return_names":"Olivia & Matteo","return_address":"12 Via Amalfi · Ravello · Italy","flap_note":"With love from Ravello","liner_text":"La dolce vita begins here"} for l in SUPPORTED_LANGUAGES}),
]

# №24 — реальная развёртка конверта под Main Invitation 180 × 130 мм.
# Готовый размер: 195 × 145 мм. Ширина развёртки: 15 + 195 + 15 = 225 мм.
# Высота: верхний клапан 55 + задняя панель 145 + лицевая панель 145 = 345 мм.
CARDS_CONFIG[-1]["envelope_spec"] = {
    "finished_w_mm": 195,
    "finished_h_mm": 145,
    "flat_w_mm": 225,
    "flat_h_mm": 345,
    "side_flap_mm": 15,
    "seal_flap_mm": 55,
    "back_panel_top_mm": 55,
    "front_panel_top_mm": 200,
    "panel_w_mm": 195,
    "panel_h_mm": 145,
    "safe_inset_mm": 8,
    "fold_marker_mm": 2.5,
}

if len(CARDS_CONFIG) != EXPECTED_CARD_COUNT:
    raise RuntimeError(f"Expected exactly {EXPECTED_CARD_COUNT} cards, got {len(CARDS_CONFIG)}")

EXPECTED_NUMBERS = list(range(1, EXPECTED_CARD_COUNT + 1))
if [card["number"] for card in CARDS_CONFIG] != EXPECTED_NUMBERS:
    raise RuntimeError("Card numbers must be continuous from 1 to 24")

for card in CARDS_CONFIG:
    if set(card["translations"]) != set(SUPPORTED_LANGUAGES):
        raise RuntimeError(f"All six translations are required for {card['id']}")

CARDS_BY_ID = {card["id"]: card for card in CARDS_CONFIG}


def printable_dimensions(card):
    bleed = card.get("bleed_mm", DEFAULT_BLEED_MM)
    return {
        "trim_w_mm": card["w_mm"],
        "trim_h_mm": card["h_mm"],
        "page_w_mm": card["w_mm"] + bleed * 2,
        "page_h_mm": card["h_mm"] + bleed * 2,
        "bleed_mm": bleed,
    }
