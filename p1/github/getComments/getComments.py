import requests
import csv
from datetime import datetime, timedelta, date
import psycopg2
import json
import logging
import pandas as pd
import os
import time
import sys

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, 'logs', f"github_comments_{sys.argv[1]}_{date.today()}.log")
tokencsv_file_path = os.path.abspath(os.path.join( 'github', 'config', f"github_token_{sys.argv[1]}.csv"))
repos_file_path = os.path.abspath(os.path.join('github', 'config', f"repos_{sys.argv[1]}.csv"))

logging.basicConfig(filename = log_file_path, level = logging.DEBUG, format = "%(asctime)s %(message)s")

error_in_execution = False

# Database connection parameters
db_params = {
    'dbname': 'socialmedia',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',  
    'port': '5432'       
}

def establish_db_connection():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except Exception as e:
        logging.error("Error while establishing a database connection:", e)
        # print("Error while establishing a database connection:", e)
        global error_in_execution
        error_in_execution = True
        return None

def check_if_comment_exist_in_db(conn, jsonObj, num):
    # Define the SELECT query
    select_query = f"SELECT * FROM github_comments where issue_number = {num} and comment_id = {jsonObj['id']};"
    # Create a cursor object
    cursor = conn.cursor()
    # Execute the SELECT query
    cursor.execute(select_query)
    # Fetch all rows
    rows = cursor.fetchall()
    return len(rows) == 0

def insert_data(conn, data, issue_number, repo_name):
    try:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO github_comments (
            issue_number,
            comment_id,
            user_id,
            created_at,
            body,
            reaction_plus_1,
            reaction_minus_1,
            reaction_laugh,
            reaction_hooray,
            reaction_confused,
            reaction_heart,
            reaction_rocket,
            reaction_eyes,
            repo_name
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """
        values = (
            issue_number,
            data['id'],
            data['user']['id'],
            datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
            data['body'],
            data['reactions']['+1'],
            data['reactions']['-1'],
            data['reactions']['laugh'],
            data['reactions']['hooray'],
            data['reactions']['confused'],
            data['reactions']['heart'],
            data['reactions']['rocket'],
            data['reactions']['eyes'],
            repo_name,
        )
        cursor.execute(insert_query, values)
        conn.commit()
        # print("Data inserted successfully.")
    except Exception as e:
        logging.error("Error while inserting data:", e, data)
        global error_in_execution
        error_in_execution = True
        # print("Error while inserting data:", e )
        return False
    return True

def get_github_comments_after_date_and_time(owner, repo, personal_access_token, issue_number, specific_date_and_time):
    api_base_url = "https://api.github.com/repos/"
    url = f"{api_base_url}{owner}/{repo}/issues/{issue_number}/comments?since={specific_date_and_time}"
    headers = {
        "Authorization": f"Bearer {personal_access_token}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        comments = response.json()
        return comments
    except Exception as e:
        logging.error(f"Error fetching comments for {owner}/{repo} - url:{url} : {e}")
        # print(f"Error fetching issues for {owner}/{repo}: {e}")
        global error_in_execution
        error_in_execution = True
        return None

def calculate_t_minus_x_mins(x):
    # Calculate the specific_date_and_time as current time minus 10 minutes
    current_time = datetime.now()
    x_minutes_ago = current_time - timedelta(minutes=x)
    return x_minutes_ago

def get_issue_numbers(conn, repo_name):
    # Define the SELECT query
    select_query = "SELECT issue_number FROM github_issues where repo_name = %s and state = 'open' and created_dt >= CURRENT_DATE - INTERVAL '30 days';"   
        
    try:
        # Create a cursor object
        cursor = conn.cursor()
        # Execute the SELECT query
        cursor.execute(select_query, (repo_name,))

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
        

def main():
    # Establish a database connection
    conn = establish_db_connection()
    if conn == None:
        return
    
    # Read config csv
    df = pd.read_csv(tokencsv_file_path)
    # Read personal access token
    personal_access_token = df['Value'][0]
    # Read comments issues 
    minutes = ((int(datetime.now().timestamp()) - int(df['Value'][1])) / 60) + 10
    logging.info(f"Fetching comments after {datetime.now()} with previous date {datetime.fromtimestamp(int(df['Value'][1]))} - ({int(df['Value'][1])}).")

    df['Value'][1] = int(datetime.now().timestamp())

    #get time
    x_mins_ago = calculate_t_minus_x_mins(minutes)

    # Read data from the CSV file
    with open(repos_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            repo_owner = row['RepoOwner']
            repo_name = row['RepoName']
            
            issue_number = get_issue_numbers(conn, f"{repo_owner}_{repo_name}")
            for num in issue_number:
                comments = get_github_comments_after_date_and_time(repo_owner, repo_name, personal_access_token, num, x_mins_ago.isoformat() + "Z")
                # print(num, comments)
                if comments is not None:
                    comments = [item for item in comments if datetime.fromisoformat(item["created_at"][:-1]) >= x_mins_ago]
                    for jsonObj in comments:

                        if check_if_comment_exist_in_db(conn, jsonObj, num):
                            if insert_data(conn, jsonObj, num, f"{repo_owner}_{repo_name}"):
                                logging.info(f"Success: Comment inserted for issue_number {num} and comment_id {jsonObj['id']}")
                            else:
                                logging.info(f"Failure: Comment insertion for issue_number {num} and comment_id {jsonObj['id']}")
                else:
                    logging.error(f"Failed to fetch comments for {repo_owner}/{repo_name}.")
                time.sleep(0.1)
                
    # # Define the SELECT query
    # select_query = "SELECT * FROM github_comments;"
    # # Create a cursor object
    # cursor = conn.cursor()
    # # Execute the SELECT query
    # cursor.execute(select_query)

    # # Fetch all rows
    # rows = cursor.fetchall()

    # # Display the results
    # for row in rows:
    #     print(row)
    if not error_in_execution:
        df.to_csv(tokencsv_file_path, index=False)

    conn.close()


if __name__ == "__main__":
    main()