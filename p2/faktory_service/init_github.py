import logging
import time
import faktory
from datetime import datetime,timedelta,date
import os
import csv
import psycopg2
from dotenv import load_dotenv

# load our .env file
load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, 'logs')
repos_file_path = os.path.abspath(os.path.join('github', 'config', 'repos.csv'))

logging.basicConfig(
    filename = log_path + f"/github_init_{date.today()}.log", level=logging.DEBUG, format="%(asctime)s %(message)s"
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

def get_github_issues_from_db(conn, repo_name):
    # Define the SELECT query
    select_query = f"SELECT issue_number FROM github_issues where repo_name = '{repo_name}';"   
        
    try:
        # Create a cursor object
        cursor = conn.cursor()
        # Execute the SELECT query
        cursor.execute(select_query)
        # Fetch all rows
        rows = cursor.fetchall()
        issue_number = []
        # Display the results
        for row in rows:
            issue_number.append(row[0])
        return issue_number
    except Exception as e:
        logging.error("Error fetching issue numbers of ", repo_name, e)
        global error_in_execution
        error_in_execution = True
        return None

def get_github_comments_from_db(conn, repo_name):
    # Define the SELECT query
    select_query = f"SELECT comment_id FROM github_comments where repo_name = '{repo_name}';"   
        
    try:
        # Create a cursor object
        cursor = conn.cursor()
        # Execute the SELECT query
        cursor.execute(select_query)
        # Fetch all rows
        rows = cursor.fetchall()
        comments_number = []
        # Display the results
        for row in rows:
            comments_number.append(row[0])
        return comments_number
    except Exception as e:
        logging.error("Error fetching issue numbers of ", repo_name, e)
        global error_in_execution
        error_in_execution = True
        return None
    

# with faktory.connection(faktory=FAKTORY_URL) as client:
#     # we need to get all issue text and comments from github
#     # remove the extra html text and put them in queue
#     conn = establish_db_connection()
#     if conn is None:
#         logging.error("Error while establishing a database connection")
#         exit(1)
#    select_query = f"SELECT number FROM github_issues where repo_name = '{repo_name}' and created_dt >= CURRENT_DATE - 2;"   

def main():
    # Establish a database connection
    conn = establish_db_connection()
    if conn == None:
        return
    # Read data from the CSV file   
    with open(repos_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            repo_owner = row['RepoOwner']
            repo_name = row['RepoName']
            issue_number = get_github_issues_from_db(conn, repo_owner + "_" + repo_name)
            table = 'github_issues'
            id_key = 'issue_number'
            text_keys = ['title','body']
            for num in issue_number:
                with faktory.connection(faktory=FAKTORY_URL) as client:
                    client.queue("toxicservice", args=(table,id_key,text_keys,num), queue="toxicservice", reserve_for=60)
                time.sleep(0.05)
            
            
            comment_id = get_github_comments_from_db(conn, repo_owner + "_" + repo_name)
            table = 'github_comments'
            id_key = 'comment_id'
            text_keys = ['body']
            for num in comment_id:
                with faktory.connection(faktory=FAKTORY_URL) as client:
                    client.queue("toxicservice", args=(table,id_key,text_keys,num), queue="toxicservice", reserve_for=60)
                time.sleep(0.05)

            
        

if __name__ == "__main__":
    main()    
# SELECT issue_number FROM github_issues where created_dt >= CURRENT_DATE - 2;