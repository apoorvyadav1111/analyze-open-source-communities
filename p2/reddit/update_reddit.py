from reddit import RedditClient
from config import SubredditConfig
import time
import logging
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

class UpdatePostCrawler:
    def __init__(self,conn, exlude_subreddits=[]):
        self.redditclient = RedditClient()
        self.subreddit_config = SubredditConfig()
        self.subreddits = self.subreddit_config.subreddits
        self.conn = conn
        self.exlude_subreddits = exlude_subreddits
    
    def update_posts(self):
        
        for subreddit in self.subreddits:
            if subreddit in self.exlude_subreddits:
                continue
            print(f"Updating posts for {subreddit}")
            if not self.update_post_for_subreddit(subreddit):
                return False
            print(f"Updated posts for {subreddit}")
        return True
    
    def update_comments(self):

        for subreddit in self.subreddits:
            if subreddit in self.exlude_subreddits:
                continue
            print(f"Updating comments for {subreddit}")
            if not self.update_comment_for_subreddit(subreddit):
                return False
            print(f"Updated comments for {subreddit}")
        return True

    def get_post_from_database(self,subreddit):
        select_query = f"SELECT post_name FROM reddit_posts where subreddit = '{subreddit}' and inserted_at > now() - interval '7 day';"
        try:
            cursor = self.conn.cursor()
            cursor.execute(select_query)
            records = cursor.fetchall()

            posts = []
            for row in records:
                posts.append(row[0])
            return posts
        except psycopg2.Error as e:
            logging.error("Update Post Service: Error while fetching posts:", e)
            return None

    def get_comment_from_database(self,subreddit):
        select_query = f"SELECT comment_id FROM reddit_comments where subreddit = '{subreddit}' and inserted_at > now() - interval '7 day';"
        try:
            cursor = self.conn.cursor()
            cursor.execute(select_query)
            records = cursor.fetchall()

            comments = []
            for row in records:
                comments.append(row[0])
            return comments
        except psycopg2.Error as e:
            logging.error("Update Comment Service: Error while fetching Comments:", e)
            return None

    def update_post_for_subreddit(self, subreddit):
        # read all posts from subreddit from database
        posts = self.get_post_from_database(subreddit)
        posts_update = []
        i = 0
        while i < len(posts):
            ids = posts[i:i+100]
            res = self.redditclient.get_detail(subreddit=subreddit,kind='POST',ids=ids)
            time.sleep(1)
            if res is None:
                continue
            if res['kind'] != 'Listing':
                continue
            for data in res['data']['children']:
                posts_update.append((data['data']['name'],data['data']))
            i += min(100, len(posts)-i)
        
        return self.update_post_in_database(subreddit,posts_update)
    
    def update_comment_for_subreddit(self, subreddit):
        # read all comments from subreddit from database
        comments = self.get_comment_from_database(subreddit)
        comments_update = []

        i = 0
        while i < len(comments):
            ids = comments[i:i+100]
            res = self.redditclient.get_detail(subreddit=subreddit,kind='COMMENT',ids=ids)
            time.sleep(1)
            if res is None:
                continue
            if res['kind'] != 'Listing':
                continue
            for data in res['data']['children']:
                comments_update.append((data['data']['id'],data['data']))
            i += min(100, len(comments)-i)
        return self.update_comment_in_database(subreddit,comments_update)

    def update_post_in_database(self,subreddit,update_posts):
        try:
            for post, data in update_posts:
                # print(post,data['score'],data['upvote_ratio'],data['ups'],data['downs'])
                update_query = f"UPDATE reddit_posts SET score = {data['score']}, upvote_ratio = {data['upvote_ratio']}, ups = {data['ups']}, downs = {data['downs']} WHERE post_name = '{post}' and subreddit='{subreddit}';"
                cursor = self.conn.cursor()
                cursor.execute(update_query)
                self.conn.commit()
            logging.info("Update Post Service: Posts updated successfully")    
            return True
        except psycopg2.Error as e:
            logging.error("Update Post Service: Error while updating posts:", e)
            return None
    
    def update_comment_in_database(self,subreddit,update_comments):
        try:
            for comment, data in update_comments:
                # print(comment,data['score'],data['ups'],data['downs'])  
                update_query = f"UPDATE reddit_comments SET score = {data['score']}, ups = {data['ups']}, downs = {data['downs']} WHERE comment_id = '{comment}' and subreddit='{subreddit}';"
                cursor = self.conn.cursor()
                cursor.execute(update_query)
                self.conn.commit()
            logging.info("Update Comment Service: Comments updated successfully")    
            return True
        except psycopg2.Error as e:
            logging.error("Update Comment Service: Error while updating comments:", e)
            return None

def main():
    
    # Check for file done.txt, if done.txt exists, then exit


    # Establish a database connection
    conn = establish_db_connection()
    if conn == None:
        logging.error("Error while establishing a database connection")
        return
    
    # Create a reddit crawler object
    exclude = 'politics'
    reddit = UpdatePostCrawler(conn, exclude)

    if not os.path.exists(log_path+f'/post_done_{date.today()}.txt'):
        if not reddit.update_posts():
            logging.error("Error while updating posts")
        else:
            # create done_post_{todays_date}.txt file to mark the date of completion
            with open(log_path+f'/post_done_{date.today()}.txt', 'w') as f:
                f.write('done')
    else:
        print("Post already updated")
    
    if not os.path.exists(log_path+f'/comment_done_{date.today()}.txt'):
        if not reddit.update_comments():
            logging.error("Error while updating comments")
        else:
            # create done_comment_{todays_date}.txt file to mark the date of completion
            with open(log_path+f'/comment_done_{date.today()}.txt', 'w') as f:
                f.write('done')
    else:
        print("Comment already updated")

    reddit.conn.close()

if __name__ == "__main__":
    main()







    
