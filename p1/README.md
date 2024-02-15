[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/_WcIwctJ)
# Analytical Approach in Making Technical Stack Selection
### Steps to run:
Each source has an independent schedule Python program that runs the collection program after a predefined schedule. This ensures isolation in case of any issues. In order to run the data collection system for the project, please find the below steps.

1. Github
   ```
   nohup python3 -u scheduleGithub.py > {yyyymmdd}github.log &
   ```

2. Reddit
   ```
   nohup python3 -u scheduleReddit.py > {yyyymmdd}reddit.log &
   ```

The above log files are related to the schedular program. For individual services, the logs are generated using <i>logging</i> package in the logs folder of the project.

### Design
<img width="839" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-1-implementation-ayadav7-arasal2/assets/113153292/c6439cab-6869-4921-be4b-52d7d2892d90">

### Directory Structure

1. github

This contains the code for collecting github data. 

  - config: configuration files for the crawler such as token, repos to crawl, previous crawl time.
  - getComments: contains code for getting comments for open issues.
  - getIssues: contains code for getting new issues.
  - updateIssueStatus: contains code to mark an issue closed. This ensures that we get comments only for open issues and thus help us stay in rate limit.

2. reddit

This folder contains code for collecting reddit data.
- config: files containing data related to token, auth, subreddits to crawl.
- logs: files containing run logs for debug as well previous id. previous ids can be used to crawl using ```before``` parameter of the api.
- sql: contains DDL for the tables being used to store.
- reddit.py: contains code for reddit crawler. get_posts and get_comments are made more generic for the purpose of design but are being used only in one manner. We use the mode='new' for posts and get all new comments for a subreddit. However, same function can be used to get comments related to a specific post. Similarly, we can get posts using different acceptable modes from reddit using the same method.
- main.py: driver file to get data from reddit.

3. scheduleGithub.py

runs the different python programs to close issues, get new issues and get comments.

5. scheduleReddit.py
   
runs the reddit crawler every 60 seconds to get data.

7. backup.sh

creates a backup of data stored in <b>socialmedia</b> database
   
