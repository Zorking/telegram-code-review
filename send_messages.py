import logging
from random import randint

import requests
import telebot
from telebot import apihelper
import sqlite3

from settings import GITLAB_TOKEN, BOT_API_KEY, PROXY, DB_PATH, PROJECT_IDS, GITLAB_URL, NUMBER_OF_REVIEWERS

logging.basicConfig(filename='logs.log', level=logging.INFO, format='[%(asctime)s] %(message)s')
logging.FileHandler(filename='logs.log', mode='w')
logging.getLogger().addHandler(logging.StreamHandler())

connection = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = connection.cursor()

apihelper.proxy = {"https": PROXY}

bot = telebot.TeleBot(token=BOT_API_KEY)


def define_approvers():
    cursor.execute("SELECT * FROM developer")
    developers = cursor.fetchall()
    if len(developers) < NUMBER_OF_REVIEWERS:
        print("Not enough developers in DB")
        exit(1)
    projects = PROJECT_IDS
    request_params = {"private_token": GITLAB_TOKEN, "state": "opened"}
    approvers = {chat_id: {"username": gitlab_username} for chat_id, _, gitlab_username in developers}
    for project_id in projects:
        url = "{}projects/{}/merge_requests".format(GITLAB_URL, project_id)
        response = requests.get(url, params=request_params).json()
        for merge_request in response:
            if merge_request.get("work_in_progress"):
                continue
            approvers = assign_merge_request(developers, merge_request, approvers)
    return approvers


def send_messages(approvers):
    for chat_id, user_info in approvers.items():
        username = user_info.get("username")
        messages = user_info.get("messages")
        if not messages:
            continue
        links = [x.get("web_url") for x in messages]
        message = "\n".join(links)
        message = "Review:\n{}".format(message)
        bot.send_message(chat_id, message)
        logging.info('{} has received {}'.format(username, ', '.join(links)))


def assign_merge_request(developers, merge_request, users):
    approvers = []
    for _ in range(NUMBER_OF_REVIEWERS):
        chat_id, username, counter = None, None, 0
        while not chat_id or is_correct_reviewer(username, merge_request, chat_id, approvers):
            chat_id = developers[randint(0, len(developers) - 1)][0]
            username = users[chat_id].get("username")
            counter += 1
            if counter > 10:
                print("Not enough developers in DB")
                exit(1)
        users = update_users(users, chat_id, merge_request)
        approvers.append(chat_id)
    return users


def update_users(users, chat_id, merge_request):
    user = users.get(chat_id)
    if user.get("messages"):
        messages = user.get("messages")
        messages.append(merge_request)
        user["messages"] = messages
    else:
        user["messages"] = [merge_request]
    users[chat_id] = user
    return users


def is_correct_reviewer(username, merge_request, chat_id, assined_reviewers):
    return username == merge_request.get("author", {}).get("username") or chat_id in assined_reviewers


if __name__ == "__main__":
    approvers = define_approvers()
    send_messages(approvers)
