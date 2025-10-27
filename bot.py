import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

USER_FILE = "users.json"

# Load user IDs
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = []

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users.append(user_id)
        save_users()
    await update.message.reply_text("✅ You are registered to receive messages from the group.")

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    sender = msg.from_user
    chat = msg.chat

    # Logging
    if msg.text:
        print(f"[Text] From {sender.id} in {chat.title}: {msg.text}")
    elif msg.photo:
        print(f"[Photo] From {sender.id} in {chat.title}")
    elif msg.video:
        print(f"[Video] From {sender.id} in {chat.title}")
    elif msg.document:
        print(f"[Document] From {sender.id} in {chat.title}")
    elif msg.sticker:
        print(f"[Sticker] From {sender.id} in {chat.title}")

    # Forward to all users
    for user_id in users:
        try:
            if msg.text:
                await context.bot.send_message(chat_id=user_id, text=msg.text)
            elif msg.photo:
                await context.bot.send_photo(chat_id=user_id, photo=msg.photo[-1].file_id, caption=msg.caption)
            elif msg.video:
                await context.bot.send_video(chat_id=user_id, video=msg.video.file_id, caption=msg.caption)
            elif msg.document:
                await context.bot.send_document(chat_id=user_id, document=msg.document.file_id, caption=msg.caption)
            elif msg.sticker:
                await context.bot.send_sticker(chat_id=user_id, sticker=msg.sticker.file_id)
        except Exception as e:
            print(f"Failed to forward to {user_id}: {e}")

def main():
    TOKEN = os.environ.get("TOKEN")
    if not TOKEN:
        print("Error: TOKEN not found!")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.GROUP & (~filters.COMMAND), forward_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
