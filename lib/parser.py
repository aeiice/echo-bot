import re

VALID_PETS = {
    "luna": "Luna",
    "mochi": "Mochi"
}


def parse_weight(text):

    text = text.strip().lower()

    pattern = r"^([a-z]+)\s+([\d.]+)\s*(kg|g)?$"

    match = re.match(pattern, text)

    if not match:
        return None

    pet = match.group(1)

    if pet not in VALID_PETS:
        return "UNKNOWN_PET"

    value = float(match.group(2))

    unit = match.group(3)

    if unit == "kg":
        grams = round(value * 1000)

    else:
        grams = round(value)

    return VALID_PETS[pet], grams
