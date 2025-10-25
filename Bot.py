# Bot.py

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import os, random

# ===========================
# Config
# ===========================
TOKEN = "8374053974:AAG9tnvVGyAPGpkBotDptsNpDSImTtY_xbI"
GROUP_ID = -1003249293736  # তোমার group chat id

# Local folder structure
categories = {
    "fruits": "images/fruits",
    "junk_food": "images/junk_food",
    "normal_food": "images/normal_food"
}

# ===========================
# Step 1: Handle photos from group
# ===========================
async def group_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return

    if update.message.photo:
        caption = (update.message.caption or "").lower()

        # classify image
        if "fruit" in caption:
            folder = categories["fruits"]
        elif "junk" in caption:
            folder = categories["junk_food"]
        else:
            folder = categories["normal_food"]

        os.makedirs(folder, exist_ok=True)

        file_id = update.message.photo[-1].file_id
        new_file = await context.bot.get_file(file_id)
        file_path = os.path.join(folder, f"{file_id}.jpg")
        await new_file.download_to_drive(file_path)
        print(f"Saved image to {file_path}")

# ===========================
# Step 2: Handle user requests
# ===========================
async def user_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.lower()

    # Simple chat responses
    if text in ["hello", "hi", "hey"]:
        await context.bot.send_message(chat_id=chat_id, text="Hello! How are you?")
        return
    if text in ["how are you", "how's it going"]:
        await context.bot.send_message(chat_id=chat_id, text="I am fine, thank you!")
        return

    # Photo requests
    if "fruit" in text:
        folder = categories["fruits"]
    elif "junk" in text:
        folder = categories["junk_food"]
    elif "food" in text:
        folder = categories["normal_food"]
    elif "give me more" in text:
        folder = None  # just resend random from all categories
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"You said: {text}")
        return

    # Gather images
    selected_images = []
    if folder:
        os.makedirs(folder, exist_ok=True)
        selected_images = os.listdir(folder)
    else:
        # merge all images
        for f in categories.values():
            if os.path.exists(f):
                selected_images.extend(os.listdir(f))

    if selected_images:
        for file_name in random.sample(selected_images, min(5, len(selected_images))):
            # find folder containing file
            for f, path in categories.items():
                if os.path.exists(os.path.join(path, file_name)):
                    file_path = os.path.join(path, file_name)
                    await context.bot.send_photo(chat_id=chat_id, photo=open(file_path, "rb"))
                    break
        await context.bot.send_message(chat_id=chat_id, text="Type 'give me more' if you want more photos.")
    else:
        await context.bot.send_message(chat_id=chat_id, text="No photos available yet.")

# ===========================
# Main function
# ===========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Handler for new photos in group
    app.add_handler(MessageHandler(filters.PHOTO, group_photo_handler))

    # Handler for user text messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), user_request_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
