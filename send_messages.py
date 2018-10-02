import os
from random import randint

import requests
import telebot
from telebot import apihelper
import sqlite3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
conn = sqlite3.connect(os.getenv("DB_PATH"), check_same_thread=False)
cursor = conn.cursor()

apihelper.proxy = {'https': os.getenv("PROXY")}

bot = telebot.TeleBot(token=os.getenv("BOT_API_KEY"))


def send_msg():
    cursor.execute("SELECT * FROM groups")
    rows = cursor.fetchall()
    projects = os.getenv("PROJECTS_ID").split(', ')
    params = {'private_token': os.getenv("GITLAB_TOKEN"), 'state': 'opened'}
    users = {x[0]: '' for x in rows}
    for project_id in projects:
        url = 'https://gitlab.com/api/v4/projects/{}/merge_requests'.format(project_id)
        w = requests.get(url, params=params).json()
        for x in w:
            if not x.get('work_in_progress'):
                user_id = rows[randint(0, len(rows) - 1)][0]
                users = update_users(users, user_id, x)
                second_id = rows[randint(0, len(rows) - 1)][0]
                while second_id == user_id:
                    second_id = rows[randint(0, len(rows) - 1)][0]
                users = update_users(users, second_id, x)

    for user_id, messages in users.items():
        messages = messages.get('messages')
        links = [x.get('web_url') for x in messages]
        message = '\n'.join(links)
        bot.send_message(user_id, message)


def update_users(users, user_id, x):
    user = users.get(user_id) or {}

    if user.get('messages'):
        q = user.get('messages')
        q.append(x)
        user['messages'] = q
    else:
        user['messages'] = [x]
    users[user_id] = user
    return users


if __name__ == '__main__':
    send_msg()
