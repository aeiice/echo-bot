import os
import json
from datetime import datetime, timedelta

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_worksheet():
    try:
        service_account = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])

        credentials = Credentials.from_service_account_info(
            service_account,
            scopes=SCOPES
        )

        client = gspread.authorize(credentials)

        spreadsheet = client.open("chonkypigs")

        worksheet = spreadsheet.worksheet("Weights")

        return worksheet

    except Exception as e:
        print("========== GOOGLE SHEETS ERROR ==========")
        print(type(e).__name__)
        print(str(e))
        raise


def save_weight(pet, grams):

    worksheet = get_worksheet()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    worksheet.append_row([
        timestamp,
        pet,
        grams,
        ""
    ])


def latest_weight(pet):

    worksheet = get_worksheet()

    rows = worksheet.get_all_records()

    pet_rows = [
        row for row in rows
        if row["Pet"].lower() == pet.lower()
    ]

    if not pet_rows:
        return None

    return pet_rows[-1]

def get_pets_sheet():
    service_account = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])

    credentials = Credentials.from_service_account_info(
        service_account,
        scopes=SCOPES
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open("chonkypigs")

    return spreadsheet.worksheet("Pets")


def get_pet_list():

    sheet = get_pets_sheet()

    values = sheet.col_values(1)

    if len(values) <= 1:
        return []

    return [pet.strip() for pet in values[1:] if pet.strip()]


def add_pet(name):

    sheet = get_pets_sheet()

    pets = [p.lower() for p in get_pet_list()]

    if name.lower() in pets:
        return False

    sheet.append_row([name.title()])

    return True

def get_week(pet):

    worksheet = get_worksheet()

    rows = worksheet.get_all_records()

    cutoff = datetime.now() - timedelta(days=7)

    results = []

    for row in rows:

        if row["Pet"].lower() != pet.lower():
            continue

        timestamp = datetime.strptime(
            row["Timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )

        if timestamp >= cutoff:
            results.append(row)

    results.sort(
        key=lambda r: datetime.strptime(
            r["Timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )
    )

    return results

def get_month(pet):

    worksheet = get_worksheet()

    rows = worksheet.get_all_records()

    cutoff = datetime.now() - timedelta(days=30)

    results = []

    for row in rows:

        if row["Pet"].lower() != pet.lower():
            continue

        timestamp = datetime.strptime(
            row["Timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )

        if timestamp >= cutoff:
            results.append(row)
            
    results.sort(
        key=lambda r: datetime.strptime(
            r["Timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )
    )

    return results
