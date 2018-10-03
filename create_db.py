import sqlite3

from settings import DB_PATH

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()
cursor.execute("""CREATE TABLE developer
                  (chat_id char (255), telegram_username char (255), gitlab_username char (255))
               """)
connection.commit()
