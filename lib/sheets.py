import os
import json
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

SERVICE_ACCOUNT = json.loads(
    os.environ["GOOGLE_SERVICE_ACCOUNT"]
)

credentials = Credentials.from_service_account_info(
    SERVICE_ACCOUNT,
    scopes=SCOPES
)

client = gspread.authorize(credentials)

# Spreadsheet name
spreadsheet = client.open("chonkypigs")

# Worksheet (tab) name
worksheet = spreadsheet.worksheet("Weights")


def save_weight(pet, grams):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    worksheet.append_row([
        timestamp,
        pet,
        grams,
        ""
    ])
