import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

PROXY = os.getenv("PROXY")
BOT_API_KEY = os.getenv("BOT_API_KEY")
PROJECT_IDS = os.getenv("PROJECT_IDS").split(', ')
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
DB_PATH = os.getenv("DB_PATH")
GITLAB_URL = "https://gitlab.com/api/v4/"
NUMBER_OF_REVIEWERS = 2