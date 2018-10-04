import logging

import requests
import telebot
from telebot import apihelper
import sqlite3

from settings import DB_PATH, PROXY, BOT_API_KEY, GITLAB_URL

logging.basicConfig(filename='logs.log', level=logging.INFO, format='[%(asctime)s] %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

apihelper.proxy = {"https": PROXY}

bot = telebot.TeleBot(token=BOT_API_KEY)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    chat = message.chat
    cursor.execute("SELECT * from developer where chat_id=(?)", (chat.id,))
    users = cursor.fetchall()
    if users:
        bot.send_message(chat.id, "Chat ID already exists in DB")
        return
    username = message.text
    if "@" in username:
        username = username.replace("@", "")
    response = requests.get("{}users?username={}".format(GITLAB_URL, username)).json()
    if not response:
        bot.send_message(chat.id, "Please enter your gitlab login")
        return
    cursor.execute("""INSERT INTO developer (chat_id, telegram_username, gitlab_username)
                      VALUES (?,?,?)""", (chat.id, chat.username, username))
    conn.commit()
    bot.send_message(chat.id, "Registration is complete. Thanks!")
    logging.info("{} has completed registration".format(username))


if __name__ == "__main__":
    print("Bot is working")
    bot.polling()
