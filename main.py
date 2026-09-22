import os
import sqlite3
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# База клиентов
db = sqlite3.connect('fitline.db', check_same_thread=False)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, username TEXT, goal TEXT, status TEXT, date TEXT, last_msg TEXT)')
db.commit()

def save(uid, name, username, msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("SELECT * FROM clients WHERE user_id=?", (uid,))
    if c.fetchone() is None:
        c.execute("INSERT INTO clients (user_id,name,username,goal,status,date,last_msg) VALUES (?,?,?,?,?,?,?)",
                  (uid, name, username, "неизвестно", "лид", now, msg))
    else:
        c.execute("UPDATE clients SET last_msg=?, date=? WHERE user_id=?", (msg, now, uid))
    db.commit()

kb = ReplyKeyboardMarkup([
    ["📸 Контент", "📅 Постинг"],
    ["📊 Маркетинг", "👥 Команда"],
    ["🏢 ЛК", "🔔 Акции"],
    ["🏷️ Продукты", "📋 Клиенты"],
    ["🔧 Помощь"]
], resize_keyboard=True)

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    uid = u.effective_user.id
    name = u.effective_user.first_name
    username = u.effective_user.username or "нет"
    save(uid, name, username, "/start")
    await u.message.reply_text(f"👋 Привет, {name}!\n\nВыбери раздел:", reply_markup=kb)

async def msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    uid = u.effective_user.id
    name = u.effective_user.first_name
    username = u.effective_user.username or "нет"
    t = u.message.text
    save(uid, name, username, t)

    if t == "📸 Контент":
        await u.message.reply_text("🎬 5 идей Reels:\n1.PC\n2.Basics\n3.Rest\n4.PS\n5.New", reply_markup=kb)
    elif t == "📅 Постинг":
        await u.message.reply_text("📅 Лучшее время: 19:00-21:00", reply_markup=kb)
    elif t == "📊 Маркетинг":
        await u.message.reply_text("📊 План:\n1.3 поста/день\n2.2 Stories\n3.1 Reel\n4.Ответы в DM", reply_markup=kb)
    elif t == "👥 Команда":
        await u.message.reply_text("👥 Партнёров: 0\nНовых: 0\nОбучение: 0%", reply_markup=kb)
    elif t == "🏢 ЛК":
        await u.message.reply_text("🏢 PV: 0\nБонусы: 0€\nЗаказов: 0", reply_markup=kb)
    elif t == "🔔 Акции":
        await u.message.reply_text("🔔 Акции:\n🎁 Стартовый набор -20%\n🎁 2+1 на FitLine skin", reply_markup=kb)
    elif t == "🏷️ Продукты":
        await u.message.reply_text("🏷️ Напиши цель:\n• энергия\n• иммунитет\n• похудение\n• мышцы", reply_markup=kb)
    elif t == "📋 Клиенты":
        c.execute("SELECT name, goal, status, date FROM clients ORDER BY date DESC")
        rows = c.fetchall()
        if not rows:
            await u.message.reply_text("📋 Клиентов пока нет", reply_markup=kb)
        else:
            text = "📋 База клиентов:\n\n"
            for i, (n, g, s, d) in enumerate(rows[:20], 1):
                text += f"{i}. {n} | {g} | {s} | {d}\n"
            await u.message.reply_text(text, reply_markup=kb)
    elif t == "🔧 Помощь":
        await u.message.reply_text("🔧 /start — меню\nНапиши 'сброс пароля'", reply_markup=kb)
    else:
        m = t.lower()
        if "энерг" in m:
            c.execute("UPDATE clients SET goal=? WHERE user_id=?", ("энергия", uid)); db.commit()
            await u.message.reply_text("⚡ PC+Basics ~97€", reply_markup=kb)
        elif "иммун" in m:
            c.execute("UPDATE clients SET goal=? WHERE user_id=?", ("иммунитет", uid)); db.commit()
            await u.message.reply_text("🛡️ Basics+Rest ~93€", reply_markup=kb)
        elif "похуд" in m:
            c.execute("UPDATE clients SET goal=? WHERE user_id=?", ("похудение", uid)); db.commit()
            await u.message.reply_text("🔥 PS+Basics ~84€", reply_markup=kb)
        elif "мышц" in m:
            c.execute("UPDATE clients SET goal=? WHERE user_id=?", ("мышцы", uid)); db.commit()
            await u.message.reply_text("💪 PC+PS ~91€", reply_markup=kb)
        elif "сброс" in m or "парол" in m:
            await u.message.reply_text("🔧 Сброс пароля:\n1.pm-international.com\n2.'Забыли пароль?'\n3.Введи email", reply_markup=kb)
        else:
            await u.message.reply_text("Выбери кнопку 👇", reply_markup=kb)

print("Бот запущен!")
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
app.run_polling()