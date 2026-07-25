import os
import json
from datetime import datetime

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
