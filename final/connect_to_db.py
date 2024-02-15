import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')

def connect_to_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        # logging.error("Error while establishing a database connection:", e)
        # print("Error while establishing a database connection:", e)
        return None
