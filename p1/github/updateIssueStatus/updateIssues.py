import requests
import csv
from datetime import datetime, timedelta, date
import psycopg2
import pandas as pd
import logging
import os
import time
import sys

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, 'logs', f"github_issues_update_{sys.argv[1]}_{date.today()}.log")
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

def update_issue_status_in_db(conn, status, repo_name, issue_number):
    try:
        cursor = conn.cursor()
        update_query = """
        Update github_issues set state = %s where repo_name =     %s and issue_number = %s;
        """
        values = (
            status,
            repo_name,
            issue_number
        )
        cursor.execute(update_query, values)
        conn.commit()
    except Exception as e:
        logging.error("Error while updating status:", e, status, repo_name, issue_number)
        global error_in_execution
        error_in_execution = True
        return False
        # print("Error while inserting data:", e )
    return True

def get_github_issue_details(owner, repo, personal_access_token, issue_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    headers = {
        "Authorization": f"Bearer {personal_access_token}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        issues = response.json()
        return issues
    except Exception as e:
        logging.error(f"Error fetching issues for {owner}/{repo} - url: {url} : {e}")
        # print(f"Error fetching issues for {owner}/{repo}: {e}")
        global error_in_execution
        error_in_execution = True
        return None

def get_open_issue_numbers(conn, repo_name):
    # Define the SELECT query
    select_query = f"SELECT issue_number FROM github_issues where repo_name = '{repo_name}' and state like '%open%';"   
        
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


def main():
    # Establish a database connection
    conn = establish_db_connection()
    if conn == None:
        return
    
    # Read config csv
    df = pd.read_csv(tokencsv_file_path)
    # Read personal access token
    personal_access_token = df['Value'][0]
    
    # Read data from the CSV file
    with open(repos_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            repo_owner = row['RepoOwner']
            repo_name = row['RepoName']
            
            issue_number = get_open_issue_numbers(conn, f"{repo_owner}_{repo_name}")
            for num in issue_number:
                issue_detail = get_github_issue_details(repo_owner, repo_name, personal_access_token, num)
                # print(num, comments)
                if issue_detail is not None:
                    if issue_detail['state'] != 'open':
                        if update_issue_status_in_db(conn, issue_detail['state'], f"{repo_owner}_{repo_name}", num) :
                            logging.info(f"Success: Status updated for issue_number {num} and state {issue_detail['state']}")
                        else:
                            logging.info(f"Failure: Status update failed for issue_number {num} and state {issue_detail['state']}")
                else:
                    logging.error(f"Failed to fetch issue details for {repo_owner}/{repo_name}/{num}.")
                time.sleep(0.1)
                # print("doe")
                # return
                
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
    
    conn.close()



if __name__ == "__main__":
    main()