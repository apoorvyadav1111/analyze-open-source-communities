import logging
import time
import faktory
from datetime import datetime,timedelta, date
import os
import csv
import psycopg2
from config import SubredditConfig
from dotenv import load_dotenv

# load our .env file
load_dotenv()


script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, 'logs')
repos_file_path = os.path.abspath(os.path.join('github', 'config', 'repos.csv'))

logging.basicConfig(
    filename = log_path + f"/reddit_init_{date.today()}.log", level=logging.DEBUG, format="%(asctime)s %(message)s"
)

FAKTORY_URL = os.environ.get('FAKTORY_URL')

DATABASE_URL = os.environ.get('DATABASE_URL')

def establish_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logging.error("Error while establishing a database connection:", e)
        # print("Error while establishing a database connection:", e)
        global error_in_execution
        error_in_execution = True
        return None

def get_reddit_post_from_database(conn,subreddit):
        select_query = f"SELECT post_name FROM reddit_posts where subreddit = '{subreddit}';"
        try:
            cursor = conn.cursor()
            cursor.execute(select_query)
            records = cursor.fetchall()

            posts = []
            for row in records:
                posts.append(row[0])
            return posts
        except psycopg2.Error as e:
            logging.error("Update Post Service: Error while fetching posts:", e)
            return None

def get_reddit_comment_from_database(conn,subreddit):
        select_query = f"SELECT comment_id FROM reddit_comments where subreddit = '{subreddit}';"
        try:
            cursor = conn.cursor()
            cursor.execute(select_query)
            records = cursor.fetchall()

            comments = []
            for row in records:
                comments.append(row[0])
            return comments
        except psycopg2.Error as e:
            logging.error("Update Comment Service: Error while fetching Comments:", e)
            return None

def main():
    # Establish a database connection
    conn = establish_db_connection()
    if conn == None:
        return
    subreddit_config = SubredditConfig()
    subreddits = subreddit_config.subreddits
        
    source = 'reddit'
    # Read data from the CSV file   
    for subreddit in subreddits:
        if subreddit == 'politics':
            continue
    
        table = 'reddit_posts'
        id_key = 'post_name'
        text_keys = ['selftext','title']


        post = get_reddit_post_from_database(conn,subreddit)
        for num in post:
            with faktory.connection(faktory=FAKTORY_URL) as client:
                client.queue("toxicservice", args=(table,id_key,text_keys,num), queue="toxicservice", reserve_for=60)
            time.sleep(0.05)
        
        comment = get_reddit_comment_from_database(conn,subreddit)
        table = 'reddit_comments'
        id_key = 'comment_id'
        text_keys = ['body']
        for num in comment:
            with faktory.connection(faktory=FAKTORY_URL) as client:
                client.queue("toxicservice", args=(table,id_key,text_keys,num), queue="toxicservice", reserve_for=60)
            time.sleep(0.05)
            
            
        

if __name__ == "__main__":
    main()    