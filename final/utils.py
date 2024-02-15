
from connect_to_db import connect_to_db

def run_query(query, values=[]):
    connection = connect_to_db()
    if connection is None:
        return None
    cursor = connection.cursor()
    cursor.execute(query,values)
    data = cursor.fetchall()
    # Close the database connection
    cursor.close()
    connection.close()
    return data


def get_subreddits():
    query = """
        SELECT DISTINCT subreddit
        FROM reddit_comments
        where subreddit != 'politics'
        ORDER BY subreddit;
        """
    return run_query(query, None)

def get_repos():
    query = """
        SELECT DISTINCT repo_name
        FROM github_comments
        ORDER BY repo_name;
        """
    return run_query(query, None)
