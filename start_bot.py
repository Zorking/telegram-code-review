import telebot
from telebot import apihelper
import sqlite3

from settings import DB_PATH, PROXY, BOT_API_KEY

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
    else:
        username = message.text
        if "@" in username:
            username = username.replace("@", "")
        cursor.execute("""INSERT INTO developer (chat_id, telegram_username, gitlab_username)
                          VALUES (?,?,?)""", (chat.id, chat.username, username))
        conn.commit()
        bot.send_message(chat.id, "Registration is complete. Thanks!")


if __name__ == "__main__":
    print("Bot is working")
    bot.polling()
