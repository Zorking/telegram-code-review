from random import randint

import requests
import telebot
from telebot import apihelper
import sqlite3

from settings import GITLAB_TOKEN, BOT_API_KEY, PROXY, DB_PATH, PROJECT_IDS, GITLAB_URL, NUMBER_OF_REVIEWERS

connection = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = connection.cursor()

apihelper.proxy = {"https": PROXY}

bot = telebot.TeleBot(token=BOT_API_KEY)


def send_msg():
    cursor.execute("SELECT * FROM developer")
    developers = cursor.fetchall()
    projects = PROJECT_IDS
    request_params = {"private_token": GITLAB_TOKEN, "state": "opened"}
    users = {chat_id: {"username": gitlab_username} for chat_id, _, gitlab_username in developers}
    for project_id in projects:
        url = "{}/v4/projects/{}/merge_requests".format(GITLAB_URL, project_id)
        response = requests.get(url, params=request_params).json()
        for merge_request in response:
            users = assign_merge_request(developers, merge_request, users)

    for user_id, messages in users.items():
        messages = messages.get("messages")
        if not messages:
            continue
        links = [x.get("web_url") for x in messages]
        message = "\n".join(links)
        message = "Review:\n{}".format(message)
        bot.send_message(user_id, message)


def assign_merge_request(developers, merge_request, users):
    if not merge_request.get("work_in_progress"):
        assigned_reviewers = []
        for _ in range(NUMBER_OF_REVIEWERS):
            user_id, username = None, None
            while not user_id or is_correct_reviewer(username, merge_request, user_id, assigned_reviewers):
                user_id = developers[randint(0, len(developers) - 1)][0]
                username = users[user_id].get("username")
            users = update_users(users, user_id, merge_request)
            assigned_reviewers.append(user_id)
    return users


def update_users(users, user_id, merge_request):
    user = users.get(user_id)

    if user.get("messages"):
        messages = user.get("messages")
        messages.append(merge_request)
        user["messages"] = messages
    else:
        user["messages"] = [merge_request]
    users[user_id] = user
    return users


def is_correct_reviewer(username, x, user_id, assined_reviewers):
    return username == x.get("author", {}).get("username") or user_id in assined_reviewers


if __name__ == "__main__":
    send_msg()
