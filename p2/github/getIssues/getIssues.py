import requests
import csv
from datetime import datetime, timedelta, date
import psycopg2
import json
import pandas as pd
import logging
import os
from dotenv import  load_dotenv

load_dotenv()
FAKTORY_URL = os.environ.get('FAKTORY_URL')

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, 'logs', f"github_issues__{date.today()}.log")
tokencsv_file_path = os.path.abspath(os.path.join( 'github', 'config', 'github_token.csv'))
repos_file_path = os.path.abspath(os.path.join('github', 'config', 'repos.csv'))

logging.basicConfig(filename = log_file_path, level = logging.DEBUG, format = "%(asctime)s %(message)s")

error_in_execution = False

# Database connection parameters
db_params = {
    'dbname': 'testenv',
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

def check_if_issue_exist_in_db(conn, jsonObj):
    # Define the SELECT query
    select_query = f"SELECT * FROM github_issues where issue_id = {jsonObj['id']};"
    # Create a cursor object
    cursor = conn.cursor()
    # Execute the SELECT query
    cursor.execute(select_query)
    # Fetch all rows
    rows = cursor.fetchall()
    return len(rows) == 0

def insert_data(conn, data, repo_name):
    try:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO public.github_issues (
            repo_name,
            issue_id,
            issue_number,
            title,
            body,
            reactions_plus_1,
            reactions_minus_1,
            reaction_laugh,
            reaction_hooray,
            reaction_confused,
            reaction_heart,
            reaction_rocket,
            reaction_eyes,
            posted_user_id,
            posted_user_username,
            labels,
            state,
            assignee,
            number_of_comments,
            created_dt,
            updated_at,
            closed_at,
            author_association
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        );
        """
        values = (
            repo_name,
            data['id'],
            data['number'],
            data['title'],
            data['body'],
            data['reactions']['+1'],
            data['reactions']['-1'],
            data['reactions']['laugh'],
            data['reactions']['hooray'],
            data['reactions']['confused'],
            data['reactions']['heart'],
            data['reactions']['rocket'],
            data['reactions']['eyes'],
            data['user']['id'],
            data['user']['login'],
            json.dumps([label['name'] for label in data['labels']]),
            data['state'],
            data['assignee'] if data['assignee'] is None else data['assignee']['id'],
            data['comments'],
            datetime.strptime(data['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
            datetime.strptime(data['updated_at'], '%Y-%m-%dT%H:%M:%SZ'),
            None if data['closed_at'] is None else datetime.strptime(data['closed_at'], '%Y-%m-%dT%H:%M:%SZ'),
            data['author_association']
        )
        cursor.execute(insert_query, values)
        conn.commit()
        # print("Data inserted successfully.")
        # enqueue toxicity calculation
        with faktory.connection(FAKTORY_URL) as client:
            client.queue("toxicservice", args=("github_issues", "issue_number", ['title',"body"], data['number']), queue="toxicservice", reserve_for=60)
    except Exception as e:
        logging.error("Error while inserting data:", e, data)
        global error_in_execution
        error_in_execution = True
        return False
        # print("Error while inserting data:", e )
    return True

def get_github_issues(owner, repo, personal_access_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
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

def calculate_t_minus_x_mins(x):
    # Calculate the specific_date_and_time as current time minus 10 minutes
    current_time = datetime.now()
    x_minutes_ago = current_time - timedelta(minutes=x)
    return x_minutes_ago

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
    minutes = ((int(datetime.now().timestamp()) - int(df['Value'][2])) / 60) + 10
    logging.info(f"Fetching issues after {datetime.now()} with previous date {datetime.fromtimestamp(int(df['Value'][1]))} - ({int(df['Value'][1])}).")

    df['Value'][2] = int(datetime.now().timestamp())

    #get time
    x_mins_ago = calculate_t_minus_x_mins(minutes)

    # Read data from the CSV file
    with open(repos_file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            repo_owner = row['RepoOwner']
            repo_name = row['RepoName']

            issues = get_github_issues(repo_owner, repo_name, personal_access_token)

            if issues is not None:
                issues = [item for item in issues if datetime.fromisoformat(item["created_at"][:-1]) >= x_mins_ago]
                for jsonObj in issues:
                    if check_if_issue_exist_in_db(conn, jsonObj):
                        if insert_data(conn, jsonObj, f"{repo_owner}_{repo_name}"):
                            logging.info(f"Success: Issue inserted for repo_name {repo_name} and issue_id {jsonObj['id']}")
                        else:
                            logging.info(f"Failure: Issue insertion for repo_name {repo_name} and issue_id {jsonObj['id']}")

            else:
                logging.error(f"Failed to fetch issues for {repo_owner}/{repo_name}.")
                print()
    # # Define the SELECT query
    # select_query = "SELECT * FROM github_issues;"
    # # Create a cursor object
    # cursor = conn.cursor()
    # # Execute the SELECT query
    # cursor.execute(select_query)

    # # Fetch all rows
    # rows = cursor.fetchall()

    # # Display the results
    # for row in rows:
    #     print(row)
    #     print()

    if not error_in_execution:
        df.to_csv(tokencsv_file_path, index=False)
    
    conn.close()


if __name__ == "__main__":
    main()