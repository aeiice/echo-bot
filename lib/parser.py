import re

from lib.sheets import get_pet_list


def parse_weight(text):

    text = text.strip()

    pattern = r"^(.+?)\s+([\d.]+)\s*(kg|g)?$"

    match = re.match(pattern, text, re.IGNORECASE)

    if not match:
        return None

    pet_name = match.group(1).strip()
    value = float(match.group(2))
    unit = (match.group(3) or "g").lower()

    pets = get_pet_list()

    real_name = None

    for pet in pets:
        if pet.lower() == pet_name.lower():
            real_name = pet
            break

    if real_name is None:
        return "UNKNOWN_PET"

    grams = round(value * 1000) if unit == "kg" else round(value)

    return real_name, grams
