class SubredditConfig:
    def __init__(self):
        self.subreddits = [
            "typescript",
            "NixOS",
            "rust",
            "FlutterDev",
            "golang",
            "kubernetes",
            "swift"
        ]
    
    def add_subreddit(self,subreddit):
        if subreddit not in self.subreddits:
            self.subreddits.append(subreddit)
        else:
            print("Subreddit already exists")
    
    def remove_subreddit(self,subreddit):
        if subreddit in self.subreddits:
            self.subreddits.remove(subreddit)
        else:
            print("Subreddit does not exist")
           
