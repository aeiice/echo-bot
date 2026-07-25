import re

def parse_weight(text):

    text = text.strip().lower()

    pattern = r"^([a-z]+)\s+([\d.]+)\s*(kg|g)?$"

    match = re.match(pattern, text)

    if not match:
        return None

    pet = match.group(1).capitalize()

    value = float(match.group(2))

    unit = match.group(3)

    if unit == "kg":
        grams = int(value * 1000)

    else:
        grams = int(value)

    return pet, grams
