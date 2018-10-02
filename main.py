import os

import telebot
from telebot import apihelper
import sqlite3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
conn = sqlite3.connect(os.getenv("DB_PATH"), check_same_thread=False)
cursor = conn.cursor()

apihelper.proxy = {'https': os.getenv("PROXY")}

bot = telebot.TeleBot(token=os.getenv("BOT_API_KEY"))


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    chat = message.chat
    cursor.execute("""INSERT INTO groups (chat_id, username)
                      VALUES (?,?)""", (chat.id, chat.username))
    conn.commit()


bot.polling()
