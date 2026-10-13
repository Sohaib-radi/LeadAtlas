"""
Business sectors (secteurs d'activité) mapped to OpenStreetMap tags.

Each sector lists one or more (key, value) tag filters. A value of None
means "any value for this key" (e.g. every ``office=*``).
"""

SECTORS = {
    # Food & hospitality
    "restaurant": {"label": "Restaurants", "group": "Food & Hospitality", "tags": [("amenity", "restaurant")]},
    "fast_food": {"label": "Fast food", "group": "Food & Hospitality", "tags": [("amenity", "fast_food")]},
    "cafe": {"label": "Cafés", "group": "Food & Hospitality", "tags": [("amenity", "cafe")]},
    "bar": {"label": "Bars & pubs", "group": "Food & Hospitality", "tags": [("amenity", "bar"), ("amenity", "pub")]},
    "hotel": {
        "label": "Hotels & accommodation",
        "group": "Food & Hospitality",
        "tags": [("tourism", "hotel"), ("tourism", "guest_house"), ("tourism", "hostel"), ("tourism", "motel")],
    },
    "bakery": {"label": "Bakeries & pastry", "group": "Food & Hospitality", "tags": [("shop", "bakery"), ("shop", "pastry")]},
    # Retail
    "supermarket": {
        "label": "Supermarkets & grocery",
        "group": "Retail",
        "tags": [("shop", "supermarket"), ("shop", "convenience"), ("shop", "greengrocer")],
    },
    "clothes": {"label": "Clothing & shoes", "group": "Retail", "tags": [("shop", "clothes"), ("shop", "shoes")]},
    "electronics": {
        "label": "Electronics & phones",
        "group": "Retail",
        "tags": [("shop", "electronics"), ("shop", "mobile_phone"), ("shop", "computer")],
    },
    "furniture": {"label": "Furniture & home", "group": "Retail", "tags": [("shop", "furniture"), ("shop", "interior_decoration")]},
    "hardware": {"label": "Hardware & DIY", "group": "Retail", "tags": [("shop", "hardware"), ("shop", "doityourself")]},
    "jewelry": {"label": "Jewelry", "group": "Retail", "tags": [("shop", "jewelry")]},
    "florist": {"label": "Florists", "group": "Retail", "tags": [("shop", "florist")]},
    "optician": {"label": "Opticians", "group": "Retail", "tags": [("shop", "optician")]},
    "all_shops": {"label": "All shops", "group": "Retail", "tags": [("shop", None)]},
    # Health
    "pharmacy": {"label": "Pharmacies", "group": "Health", "tags": [("amenity", "pharmacy")]},
    "doctor": {"label": "Doctors & clinics", "group": "Health", "tags": [("amenity", "doctors"), ("amenity", "clinic")]},
    "dentist": {"label": "Dentists", "group": "Health", "tags": [("amenity", "dentist")]},
    "hospital": {"label": "Hospitals", "group": "Health", "tags": [("amenity", "hospital")]},
    "veterinary": {"label": "Veterinarians", "group": "Health", "tags": [("amenity", "veterinary")]},
    # Beauty & wellness
    "hairdresser": {"label": "Hairdressers & barbers", "group": "Beauty & Wellness", "tags": [("shop", "hairdresser")]},
    "beauty": {"label": "Beauty salons & spas", "group": "Beauty & Wellness", "tags": [("shop", "beauty"), ("leisure", "spa")]},
    "gym": {"label": "Gyms & fitness", "group": "Beauty & Wellness", "tags": [("leisure", "fitness_centre"), ("leisure", "sports_centre")]},
    # Professional services
    "lawyer": {"label": "Lawyers", "group": "Professional Services", "tags": [("office", "lawyer"), ("office", "notary")]},
    "accountant": {"label": "Accountants", "group": "Professional Services", "tags": [("office", "accountant"), ("office", "tax_advisor")]},
    "real_estate": {"label": "Real estate agencies", "group": "Professional Services", "tags": [("office", "estate_agent"), ("shop", "estate_agent")]},
    "insurance": {"label": "Insurance", "group": "Professional Services", "tags": [("office", "insurance")]},
    "it": {"label": "IT & software companies", "group": "Professional Services", "tags": [("office", "it"), ("office", "telecommunication")]},
    "architect": {"label": "Architects & engineers", "group": "Professional Services", "tags": [("office", "architect"), ("office", "engineer")]},
    "consulting": {"label": "Consulting & agencies", "group": "Professional Services", "tags": [("office", "consulting"), ("office", "advertising_agency")]},
    "travel_agency": {"label": "Travel agencies", "group": "Professional Services", "tags": [("shop", "travel_agency")]},
    "all_offices": {"label": "All offices / companies", "group": "Professional Services", "tags": [("office", None)]},
    # Automotive
    "car_repair": {"label": "Car repair & garages", "group": "Automotive", "tags": [("shop", "car_repair"), ("shop", "tyres")]},
    "car_dealer": {"label": "Car dealers", "group": "Automotive", "tags": [("shop", "car")]},
    "car_rental": {"label": "Car rental", "group": "Automotive", "tags": [("amenity", "car_rental")]},
    "fuel": {"label": "Fuel stations", "group": "Automotive", "tags": [("amenity", "fuel")]},
    # Finance & education
    "bank": {"label": "Banks", "group": "Finance & Education", "tags": [("amenity", "bank"), ("amenity", "bureau_de_change")]},
    "school": {"label": "Schools", "group": "Finance & Education", "tags": [("amenity", "school"), ("amenity", "kindergarten")]},
    "training": {
        "label": "Training centers & languages",
        "group": "Finance & Education",
        "tags": [("amenity", "language_school"), ("amenity", "training"), ("amenity", "driving_school")],
    },
    # Trades & industry
    "craft": {"label": "Craftsmen & trades", "group": "Trades & Industry", "tags": [("craft", None)]},
    "industrial": {"label": "Industrial & factories", "group": "Trades & Industry", "tags": [("industrial", None), ("man_made", "works")]},
}


def sector_choices():
    """Choices grouped for a <select> with <optgroup>s."""
    groups = {}
    for key, sector in SECTORS.items():
        groups.setdefault(sector["group"], []).append((key, sector["label"]))
    return [(group, options) for group, options in groups.items()]


def sector_label(key):
    sector = SECTORS.get(key)
    return sector["label"] if sector else key
