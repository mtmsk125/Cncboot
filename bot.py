import json, os, difflib
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
MY_STORE = "@BootMarketStore"
CONTACT = "@mtmk125"
DB_FILE = "files_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

files_db = load_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔥 Welcome to Boot Market Store Bot\n\n"
        f"📁 Send file name to search\n"
        f"📊 Total files: {len(files_db)}\n\n"
        f"🤖 via {MY_STORE}\n"
        f"📩 Order bot: {CONTACT}"
    )

async def add_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        fid = update.message.document.file_id
        fname = update.message.caption or update.message.document.file_name
        key = fname.lower().strip()
        files_db[key] = {"id": fid, "name": fname}
        save_db(files_db)
        await update.message.reply_text(f"✅ File saved:\n{fname}\n\nTotal: {len(files_db)}")
    elif update.message.photo:
        fid = update.message.photo[-1].file_id
        fname = update.message.caption or f"photo_{len(files_db)}.jpg"
        key = fname.lower().strip()
        files_db[key] = {"id": fid, "name": fname}
        save_db(files_db)
        await update.message.reply_text(f"✅ Photo saved:\n{fname}")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document or update.message.photo:
        return
    query = update.message.text.lower().strip()
    if len(query) < 2:
        return
    all_names = list(files_db.keys())
    matches = difflib.get_close_matches(query, all_names, n=5, cutoff=0.4)
    for name in all_names:
        if query in name and name not in matches:
            matches.append(name)
    if not matches:
        await update.message.reply_text(f"❌ File '{update.message.text}' not found\n\nOrder custom bot: {CONTACT}")
        return
    best = matches[0]
    data = files_db[best]
    caption = f"📁 {data['name']}\n\n🤖 via {MY_STORE}\n📩 Get your bot: {CONTACT}"
    try:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=data['id'], caption=caption)
    except:
        await update.message.reply_text(f"📁 {data['name']}\n\nReady!\nvia {MY_STORE}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📊 {MY_STORE} Stats\n\nTotal files: {len(files_db)}\nBot: @BootMarketStores_bot")

def main():
    print(f"🚀 Bot @BootMarketStores_bot Started [ENGLISH]...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, add_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    app.run_polling()

if __name__ == "__main__":
    main()
