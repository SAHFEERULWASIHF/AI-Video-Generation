import logging
import os
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

API_URL = os.getenv("API_URL", "http://localhost:8000")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to FSW Creations AI Reel Control Center.\nCommands:\n/generate [topic]\n/status [id]\n/accounts")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)
    if not topic:
        await update.message.reply_text("Please provide a topic: /generate [topic]")
        return

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_URL}/reels/generate", params={"topic": topic})
            data = response.json()
            await update.message.reply_text(f"🚀 Generation started for: {topic}\nReel ID: {data['reel_id']}")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reel_id = context.args[0] if context.args else None
    if not reel_id:
        await update.message.reply_text("Usage: /status [reel_id]")
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/reels/{reel_id}")
        data = response.json()

    text = f"Reel {reel_id} Status: {data['status']}\n"
    keyboard = []

    if data['status'] == 'completed':
        text += "Video is ready for review."
        keyboard = [
            [InlineKeyboardButton("Approve & Post", callback_data=f"approve_{reel_id}")],
            [InlineKeyboardButton("Reject", callback_data=f"reject_{reel_id}")]
        ]
        # In a real bot, we would send the video here
        # await update.message.reply_video(video=open(data['video_path'], 'rb'))

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await update.message.reply_text(text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, reel_id = data.split("_")

    if action == "approve":
        await query.edit_message_text(text=f"Reel {reel_id} approved. Posting to Instagram...")
        # Trigger posting via API
        async with httpx.AsyncClient() as client:
            await client.post(f"{API_URL}/reels/{reel_id}/post")
    elif action == "reject":
        await query.edit_message_text(text=f"Reel {reel_id} rejected.")

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not set.")
        exit(1)

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('generate', generate))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()
