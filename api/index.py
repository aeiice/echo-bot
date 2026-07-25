from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import os

app = Flask(__name__)

# 1. Get the Token from Vercel Environment Variables
TOKEN = os.environ.get("TOKEN")

# 2. Define the Bot Logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am an Echo Bot. I repeat everything you say.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This is where the echo magic happens
    user_text = update.message.text
    await update.message.reply_text(f"You said: {user_text}")

# 3. Setup the Application (Using the async ApplicationBuilder)
# We build it once to handle the update
async def main(update_json):
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Process the update
    # We manually initialize and process because we are in a serverless environment
    await application.initialize()
    update = Update.de_json(update_json, application.bot)
    await application.process_update(update)
    await application.shutdown()

# 4. The Webhook Route (What Vercel runs)
@app.route("/", methods=["POST"])
def webhook():
    if request.method == "POST":
        # Get the JSON data sent by Telegram
        update_json = request.get_json(force=True)
        
        # Run the async main function
        asyncio.run(main(update_json))
        
        return "ok"
    return "Bot is running!"
