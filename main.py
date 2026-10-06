import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GIGACHAT_KEY = os.getenv("GIGACHAT_KEY")

giga = GigaChat(credentials=GIGACHAT_KEY, verify_ssl_certs=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я FitLine-ассистент на GigaChat. Спроси что-нибудь про продукты."
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Думаю...")
    response = giga.chat(update.message.text)
    await update.message.reply_text(response.choices[0].message.content)

def main():
    print("Бот запущен!")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()
