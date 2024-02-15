from reddit import RedditClient
from config import SubredditConfig
import time
import logging
import pandas
import psycopg2
from datetime import datetime, date
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, 'logs')

logging.basicConfig(
    filename= log_path + f"/reddit_{date.today()}.log", level=logging.DEBUG, format="%(asctime)s %(message)s"
)  

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
    except psycopg2.Error as e:
        logging.error("Error while establishing a database connection:", e)
        # print("Error while establishing a database connection:", e)
        return None

class RedditCrawler:
    def __init__(self, conn):
        self.redditclient = RedditClient()
        self.subreddit_config = SubredditConfig()
        self.subreddits = self.subreddit_config.subreddits
        self.beforePost = dict()
        self.beforeComment = dict()
        self.conn = conn

        for subreddit in self.subreddits:
            self.beforePost[subreddit] = ''
        
        for subreddit in self.subreddits:
            self.beforeComment[subreddit] = ''
        
        # # get beforePost and beforeComment from text file
        # for subreddit in self.subreddits:
        #     with open(log_path + '/' + subreddit + '_beforePost.txt', 'r') as f:
        #         self.beforePost[subreddit] = f.read()
        #     with open(log_path + '/' +  subreddit + '_beforeComment.txt', 'r') as f:
        #         self.beforeComment[subreddit] = f.read()

        # get beforePost and beforeComment from csv
        # df = pandas.read_csv('./logs/before_post.csv')
        # for subreddit in self.subreddits:
        #     self.beforePost[subreddit] = df[df['subreddit'] == subreddit]['before'].values[0]
        #     self.beforeComment[subreddit] = df[df['subreddit'] == subreddit]['before'].values[0]





    def get_posts(self,subreddit,mode='new'):
        before = self.beforePost[subreddit]
        resp = self.redditclient.get_posts(subreddit,mode,before)
        if not resp or not resp['data']['children']:
            return

        # Insert then update
        posts = []
        for post in resp["data"]["children"]:
            posts.append({
                "subreddit": post["data"].get("subreddit"),
                "title": post["data"].get("title"),
                "selftext": post["data"].get("selftext"),
                "upvote_ratio": post["data"].get("upvote_ratio"),
                "ups": post["data"].get("ups"),
                "downs": post["data"].get("downs"),
                "score": post["data"].get("score"),
                "link_flair_text": post["data"].get("link_flair_text"),
                "created_utc": post["data"].get("created_utc"),
                "post_id": post["data"].get("id"),
                "post_name": post["data"].get("name"),
                "over_18": post["data"].get("over_18"),
                "author": post["data"].get("author"),
                "author_fullname": post["data"].get("author_fullname"),
                "url": post["data"].get("url"),
            })
        # display_posts(posts)
        if self.insert_posts(posts):
            # set before for the next request
            # self.beforePost[subreddit] = resp['data']['children'][0]['data']['name']
            logging.info("last post: {}".format(resp['data']['children'][0]['data']['name']))
            with open(log_path + '/' +  subreddit + '_beforePost.txt', 'w') as f:
                f.write(self.beforePost[subreddit])

        else:
            logging.error("Error inserting posts into db")


    def get_comments(self,subreddit,postid=''):
        before = self.beforeComment[subreddit]
        resp = self.redditclient.get_comments(subreddit,postid,before)
        if not resp or not resp['data']['children']:
            return
        
        # Insert then update
        comments = []
        for comment in resp['data']['children']:
            comments.append({
                "comment_id": comment["data"].get("id"),
                "post_name": comment["data"].get("link_id"),
                "created_utc": comment["data"].get("created_utc"),
                "author": comment["data"].get("author"),
                "author_fullname": comment["data"].get("author_fullname"),
                "body": comment["data"].get("body"),
                "ups": comment["data"].get("ups"),
                "downs": comment["data"].get("downs"),
                "score": comment["data"].get("score"),
                "subreddit": comment["data"].get("subreddit"),
                "over_18": comment["data"].get("over_18"),
            })
        
        # display_comments(comments)
        if self.insert_comments(comments):
            # set before for the next request
            # self.beforeComment[subreddit] = resp['data']['children'][0]['data']['name']
            logging.info("last comment: {}".format(resp['data']['children'][0]['data']['name']))
            with open(log_path + '/' + subreddit + '_beforeComment.txt', 'w') as f:
                f.write(self.beforeComment[subreddit])
        else:
            logging.error("Error inserting comments into db")



    def insert_posts(self,posts):

        for post in posts:
            try:
                cursor = self.conn.cursor()

                # Check if post exists
                check_query = f"SELECT * FROM reddit_posts WHERE post_id = '{post['post_id']}';"
                cursor.execute(check_query)
                if len(cursor.fetchall())>0:
                    break

                # Insert post
                insert_query = """
                INSERT INTO reddit_posts (
                            subreddit,
                            post_id,
                            post_name,
                            title,
                            selftext,
                            ups,
                            downs,
                            score,
                            upvote_ratio,
                            over_18,
                            url,
                            author,
                            author_fullname,
                            link_flair_text,
                            created_utc
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                    """
                values = (
                    post["subreddit"],
                    post["post_id"],
                    post["post_name"],
                    post["title"],
                    post["selftext"],
                    post["ups"],
                    post["downs"],
                    post["score"],
                    post["upvote_ratio"],
                    post["over_18"],
                    post["url"],
                    post["author"],
                    post["author_fullname"],
                    "" if not post["link_flair_text"] else post["link_flair_text"],
                    datetime.fromtimestamp(post["created_utc"])
                )
                cursor.execute(insert_query, values)
                self.conn.commit()
                # print("Data inserted successfully.")
            except psycopg2.Error as e:
                logging.error("Error while inserting data:", e, post)
                return False
        logging.info("Posts inserted successfully.")
        return True


        
    def insert_comments(self,comments):
        # loop over comments and insert
        for comment in comments:
            try:
                cursor = self.conn.cursor()

                # Check if comment exists
                check_query = f"SELECT * FROM reddit_comments WHERE comment_id = '{comment['comment_id']}';"
                cursor.execute(check_query)
                if len(cursor.fetchall())>0:
                    break

                # Insert comment
                insert_query = """
                INSERT INTO reddit_comments (
                            comment_id,
                            post_name,
                            created_utc,
                            author,
                            author_fullname,
                            body,
                            ups,
                            downs,
                            score,
                            subreddit,
                            over_18
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                    """
                values = (
                    comment["comment_id"],
                    comment["post_name"],
                    datetime.fromtimestamp(comment["created_utc"]),
                    comment["author"],
                    comment["author_fullname"],
                    comment["body"],
                    comment["ups"],
                    comment["downs"],
                    comment["score"],
                    comment["subreddit"],
                    comment["over_18"], 
                )
                cursor.execute(insert_query, values)
                self.conn.commit()
                # print("Data inserted successfully.")
            except psycopg2.Error as e:
                logging.error("Error while inserting data:", e, comment)
                return False
        logging.info("Comments inserted successfully.")
        return True

    
    # def get_posts_and_insert(self, subreddit):
    #     # get new posts and insert into db
    #     posts = get_posts(subreddit)
    #     # new_posts = get_new_posts(posts)
    #     # insert new posts into db


    #     # mark current set of ids as previous
    #     current = set()
    #     for post in posts:
    #         current.add(post["id"])
    #     self.previous = current
    #     pass
    
    # def get_new_posts(self, posts):
    #     new_post_set = set()
    #     for post in posts:
    #         new_post_set.add(post["id"])
    #     return new_post_set.difference(self.previous)

def display_posts(posts):
    for post in posts:
        print(post["post_id"], post["title"], post["url"])

def display_comments(comments):
    for comment in comments:
        print(comment["comment_id"], comment["post_id"],comment["body"])

def main():
    
    # Establish a database connection
    conn = establish_db_connection()
    if conn == None:
        logging.error("Error while establishing a database connection")
        return
    
    # Create a reddit crawler object
    reddit = RedditCrawler(conn)
    for subreddit in reddit.subreddits:
        reddit.get_posts(subreddit)
        time.sleep(0.1)
        reddit.get_comments(subreddit)
        time.sleep(0.1)
    
    reddit.conn.close()


if __name__ == "__main__":
    main()
