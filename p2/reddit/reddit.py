import requests
from config import RedditConfig 
import logging
import os
from datetime import date

script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, 'logs')

logging.basicConfig(
    filename = log_path + f"/reddit_{date.today()}.log", level=logging.DEBUG, format="%(asctime)s %(message)s"
)

class RedditClient:
    BASE_API_URL = "https://www.reddit.com/r"
    headers = {"User-Agent": "app1/0.0.1"}

    def __init__(self):
        self.config = RedditConfig()
        self.client_id = self.config.client
        self.client_secret = self.config.secret
        self.username = self.config.username
        self.password = self.config.password
        self.auth_api()

    def auth_api(self):
        # authenticate API
        client_auth = requests.auth.HTTPBasicAuth(
            self.client_id, self.client_secret
        )
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        headers = self.headers
        # send authentication request for OAuth token
        res = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=client_auth,
            data=data,
            headers=headers,
        )

        token = f"bearer {res.json()['access_token']}"
        headers = {**headers, **{"Authorization": token}}
        self.headers = headers
        return headers

    def get_posts(self, subreddit,mode='new', before=''):
        endpoint_url = "https://oauth.reddit.com/r/{}/{}".format(subreddit, mode)
        logging.info("Requesting {}".format(endpoint_url))
        params = {
            "limit": 100,
        }
        if before!='':
            params['before'] = before
        try:
            res = requests.get(endpoint_url,
                headers=self.headers,
                params=params
                )
            return res.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching issues for {subreddit}: {e}")
            # print(f"Error fetching issues for {owner}/{repo}: {e}")
            return None

    def get_comments(self,subreddit,postid='',before=''):
        params = {
            "limit": 100,
        }
        if before!='':
            params['before'] = before

        endpoint_url = "https://oauth.reddit.com/r/{}/comments/{}".format(subreddit, postid)
        logging.info("Requesting {} {}".format(endpoint_url, params))
        try:
            res = requests.get(endpoint_url,
                        headers=self.headers,
                        params=params
                        )
            return res.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching issues for {subreddit}/{postid}: {e}")
            # print(f"Error fetching issues for {owner}/{repo}: {e}")
            return None
        
    
    def get_detail(self,subreddit,kind,ids):
        if kind == 'POST':
            for i in range(len(ids)):
                if ids[i][:3]!='t3_':
                    ids[i] = 't3_'+ids[i]
    
        elif kind == 'COMMENT':
            for i in range(len(ids)):
                if ids[i][:3]!='t1_':
                    ids[i] = 't1_'+ids[i]
        elif kind == 'SUBREDDIT':
            for i in range(len(ids)):
                if ids[i][:3]!='t5_':
                    ids[i] = 't5_'+ids[i]
        elif kind == 'USER':
            for i in range(len(ids)):
                if ids[i][:3]!='t2_':
                    ids[i] = 't2_'+ids[i]
        else:
            return None

        endpoint_url = "https://oauth.reddit.com/r/{}/api/info.json?id={}".format(subreddit,','.join(ids))
        logging.info("Requesting for Kind: {} count:{} {} ".format(kind, len(ids),endpoint_url))

        try:
            res = requests.get(
                endpoint_url,
                headers = self.headers
            )

            return res.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching issues for {subreddit}/{id}: {e}")
            return None
        
