import faktory
import logging
from faktory import Worker
from datetime import datetime, timedelta, date
import time
import psycopg2
from dotenv import load_dotenv
import os
from moderatehatespeech.toxicityservice import ToxicityService

# these three lines allow psycopg to insert a dict into
# a jsonb coloumn
from psycopg2.extras import Json
from psycopg2.extensions import register_adapter
register_adapter(dict, Json)

# load our .env file
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
FAKTORY_URL = os.environ.get('FAKTORY_URL')
MODERATEHATESPEECH_TOKEN = os.environ.get('MODERATEHATESPEECH_TOKEN')

script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, 'logs')

logging.basicConfig(
    filename = log_path + f"/faktory_service_{date.today()}.log", level=logging.DEBUG, format="%(asctime)s %(message)s"
)


def establish_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        logging.error("Error while establishing a database connection:", e)
        # print("Error while establishing a database connection:", e)
        return None

class GetToxicityCrawler(object):
    service = ToxicityService()
    def __new__(cls, token):
        """ 
        creates a singleton object, if it is not created, 
        or else returns the previous singleton object 
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(GetToxicityCrawler, cls).__new__(cls)
        cls.instance.service.add_token(token)
        return cls.instance


def get_text_from_database(table,id_key,text_keys,id):
    # get db connection
    conn = establish_db_connection()
    if conn is None:
        return None
    
    # Define the SELECT query
    text_keys = ','.join(text_keys)

    select_query = f"SELECT {text_keys}  FROM {table} where {id_key} = '{id}' limit 1;"

    # execute the query
    try:
        # Create a cursor object
        cursor = conn.cursor()
        # Execute the SELECT query
        cursor.execute(select_query)
        # Fetch the row
        row = cursor.fetchone()
        filtered_row = [x for x in row if x is not None]

        cursor.close()
        conn.close()
        return ' '.join(filtered_row) if filtered_row is not None else ''
    except Exception as e:
        logging.error("Error fetching text from ",table, id, e)
        cursor.close()
        conn.close()
        return None
    

def get_toxicity_for_text(table,id_key,text_keys,id):
    text = get_text_from_database(table,id_key,text_keys,id)
    if text is None:
        return None
    client = GetToxicityCrawler(MODERATEHATESPEECH_TOKEN)
    response = client.service.moderate(text)
    return client.service.moderate(text)

def get_toxicity(table, id_key, text_keys, id):
    toxicity = get_toxicity_for_text(table, id_key, text_keys, id)
    if not toxicity and 'response' not in toxicity or toxicity['response'] != 'Success':
        raise Exception("Error getting toxicity for ", table, id_key, id, toxicity)
    with faktory.connection(FAKTORY_URL) as client:
        client.queue("dbservice", args=(table, id_key, id, toxicity), queue="dbservice", reserve_for=60)

def store_toxicity_in_database(table, id_key, id, toxicity):
    # get db connection
    conn = establish_db_connection()
    if conn is None:
        return None
    
    # Define the insert query
    update_query = f"INSERT INTO {table}_sentiment ({id_key}, class, confidence) VALUES (%s, %s, %s);"
    values = (id, toxicity['class'], toxicity['confidence'])

    # execute the query
    try:
        # Create a cursor object
        cursor = conn.cursor()
        # Execute the SELECT query
        cursor.execute(update_query, values)
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"updated toxicity for {table} {id_key} {id} to {toxicity}")
        return True
    except Exception as e:
        logging.error("Error updating toxicity of ", table, id_key, id, e)
        cursor.close()
        conn.close()
        raise Exception("Error updating toxicity of ", table, id_key, id, e)
        return None


if __name__ == "__main__":
    # NB: You can (and in certain circumstances probably should) increase concurrency level here.
    print("starting")
    print(f"FAKTORY_URL: {FAKTORY_URL}")
    print(f"DATABASE_URL: {DATABASE_URL}")
    print(f"TOKEN: {MODERATEHATESPEECH_TOKEN}")
    w = Worker(faktory=FAKTORY_URL, queues=["toxicservice", "dbservice"], concurrency=10, use_threads=True)
    w.register("toxicservice", get_toxicity)
    w.register("dbservice", store_toxicity_in_database)
    logging.info("running?")
    w.run()