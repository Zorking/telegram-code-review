import os
import sqlite3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
conn = sqlite3.connect(os.getenv("DB_PATH"))
cursor = conn.cursor()

# Создание таблицы
cursor.execute("""CREATE TABLE groups
                  (chat_id char (255), username char (255))
               """)

conn.commit()
