from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import asyncio
import os

from datetime import datetime

from lib.parser import parse_weight
from lib.sheets import (
    save_weight,
    add_pet,
    get_pet_list,
    get_week,
    get_month,
    delete_last_weight,
)

app = Flask(__name__)

# 1. Get the Token from Vercel Environment Variables
TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """🐹 Pig Weight Tracker

Simply send:

Butter 950g

or

Butter 0.95kg

Commands:

/addpet Butter
/listpets
/week Butter
/month Butter"""
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    result = parse_weight(text)

    if result is None:

        await update.message.reply_text(
            "❌ Invalid format.\n\nExample:\nButter 900g"
        )

        return

    if result == "UNKNOWN_PET":

        await update.message.reply_text(
            "❌ Unknown pet.\n\nUse /listpets to see available pets."
        )

        return

    pet, grams = result

    try:

        save_weight(pet, grams)

        await update.message.reply_text(
            f"""✅ Saved!

🐹 {pet}

Weight: {grams/1000:.3f} kg"""
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error\n\n{e}"
        )

async def addpet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage:\n/addpet Butter"
        )
        return

    name = " ".join(context.args).strip()

    success = add_pet(name)

    if success:
        await update.message.reply_text(
            f"✅ Added pet: {name.title()}"
        )
    else:
        await update.message.reply_text(
            f"⚠️ {name.title()} already exists."
        )

async def listpets(update: Update, context: ContextTypes.DEFAULT_TYPE):

    pets = get_pet_list()

    if len(pets) == 0:
        await update.message.reply_text(
            "No pets added yet."
        )
        return

    message = "🐹 Current pigs\n\n"

    for pet in pets:
        message += f"• {pet}\n"

    await update.message.reply_text(message)

# async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):

#     if len(context.args) == 0:

#         await update.message.reply_text(
#             "Usage:\n/week Butter"
#         )

#         return

#     pet = " ".join(context.args)

#     rows = get_week(pet)

#     if len(rows) == 0:

#         await update.message.reply_text(
#             "No records found."
#         )

#         return

#     message = f"📅 {pet.title()} - Last 7 Days\n\n"

#     for row in rows:

#         dt = datetime.strptime(
#             row["Timestamp"],
#             "%Y-%m-%d %H:%M:%S"
#         )

#         message += (
#             f"{dt.strftime('%d %b %I:%M %p')} "
#             f"- {int(row['Weight'])}g\n"
#         )

#     await update.message.reply_text(message)

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        await update.message.reply_text("DEBUG: week command received")

        if len(context.args) == 0:
            await update.message.reply_text("Usage:\n/week Butter")
            return

        pet = " ".join(context.args)

        await update.message.reply_text(f"Looking for: {pet}")

        rows = get_week(pet)

        await update.message.reply_text(f"Found {len(rows)} records")

        if len(rows) == 0:
            await update.message.reply_text("No records found.")
            return

        message = f"📅 {pet.title()} - Last 7 Days\n\n"

        for row in rows:

            await update.message.reply_text(str(row))

            dt = datetime.strptime(
                row["timestamp"],
                "%Y-%m-%d %H:%M:%S"
            )

            message += (
                f"{dt.strftime('%d %b %I:%M %p')} - "
                f"{int(row['weight'])}g\n"
            )

        await update.message.reply_text(message)

    except Exception as e:

        await update.message.reply_text(
            f"❌ {type(e).__name__}\n\n{e}"
        )

async def month(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:

        await update.message.reply_text(
            "Usage:\n/month Butter"
        )

        return

    pet = " ".join(context.args)

    rows = get_month(pet)

    if len(rows) == 0:

        await update.message.reply_text(
            "No records found."
        )

        return

    message = f"📅 {pet.title()} - Last 30 Days\n\n"

    for row in rows:

        dt = datetime.strptime(
            row["timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )

        message += (
            f"{dt.strftime('%d %b')} "
            f"- {int(row['weight'])}g\n"
        )

    await update.message.reply_text(message)

# # 2. [OLD ECHO BOT LOGIC]
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Hello! I am an Echo Bot. I repeat everything you say.")

# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # This is where the echo magic happens
#     user_text = update.message.text
#     await update.message.reply_text(f"You said: {user_text}")
# # END OF OLD ECHO BOT 

# 3. Setup the Application (Using the async ApplicationBuilder)
# We build it once to handle the update
async def main(update_json):
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addpet", addpet))
    application.add_handler(CommandHandler("listpets", listpets))
    application.add_handler(CommandHandler("week", week))
    application.add_handler(CommandHandler("month", month))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Process the update
    # We manually initialize and process because we are in a serverless environment
    await application.initialize()
    update = Update.de_json(update_json, application.bot)
    await application.process_update(update)
    await application.shutdown()

# 4. The Webhook Route (What Vercel runs)
@app.route("/", methods=["GET","POST"])
def webhook():
    if request.method == "POST":
        # Get the JSON data sent by Telegram
        update_json = request.get_json(force=True)
        
        # Run the async main function
        asyncio.run(main(update_json))
        
        return "ok"
    return "Bot is running!"
