# Analytical Approach in Making Technical Stack Selection
## Phase II
In this phase, we introduced toxicity prediction for all data records. We used https://moderatehatespeech.com/ for this. It provides more than enough API calls to meet our requirements. Until now, on average we make 6000 API calls per day. We also added updating Reddit data as part of the Reddit crawler to get the latest upvotes and scores.

### Details
1. Documentation: https://moderatehatespeech.com/docs/
2. An important thing to note is the server expects the token as part of the request params and not header.

### Implement a job queuing system
One important caveat of using moderatehatespeech is that it doesn't have 99.9999999... sort of availability and hence, if we create a tightly coupled pipeline, it would work against us. Therefore, we decided to use a job queuing system to get the predictions and then insert them into the database.  

With respect to designing queues, we decided to create a generalized service as much as possible. We are using only two sources, however, we wanted to create a toxicity prediction service that can handle any number of additional data sources without any interference with existing code. We isolated the logic to get the prediction and insert into db for the same reason.

Hence, there is only one queue to get the toxicity service, which takes, parameters to identify the data source (table name), an identifier to get the data from that table, the name of the field that is identified and a list of fields that contain the text. Some sample job parameters with a variety of sources will look like the following:
1. Reddit Post: reddit_posts,post_name, ['selftext', 'title'], t3_sadbasb
2. Reddit Comments: reddit_comments,comment_id, ['body'], t1_asdagde
3. Github Issues: github_issues,issue_number, ['body'],12313123
4. Github Comments: github_comments, comment_id, ['body'], 123123122
5. In future, an additional source such as X (twitter) can use the following params:
    twitter_data, tweet_id, ['body','title'], 1231231312

Sample code snippet
```
 client.queue("toxicservice", args=(table,id_key,text_keys,id_value), queue="toxicservice", reserve_for=60)
```

The service gets the source data by creating an SQL query using these parameters and makes an API call. Once successful, it enqueues into a queue that handles storing in the database. Again, we created only one queue that handles this. This ensures 0 change when we add YouTube, twitter, etc. 

We store sentiments into separate tables, specifically, {src_table}_sentiment. Therefore, we use parameters: table name, identifier, and result. An SQL insert query is generated using these parameters and the result is stored.

Sample code snippet
```
client.queue("dbservice", args=(table, id_key, id_value, toxicity), queue="dbservice", reserve_for=60)
```

At the end of this readme, we have listed steps to add additional sources to this service. 

#### Faktory
We used faktory to implement the system described above. In order to use it, we need a language-dependent client and an agnostic server. 
1. Steps to install server: https://github.com/contribsys/faktory/wiki/Installation
2. We used faktory_worker_python: https://github.com/cdrx/faktory_worker_python

### Updating Reddit data
We added another service in the Reddit folder to get the latest upvotes, downvotes, and score for the records in the reddit. We run this service every day once at most. We start the service every 15 minutes and check if it has already completed using a ```post_done_{date.today()}.txt``` and ```comment_done_{date.today()}.txt``` file. This ensures that retries incase the service failed during the last attempt. 

The update service uses a new endpoint added to the existing crawler. The endpoint can be used to get information for any entity on reddit and can handle multiple ids to query at once.
```
endpoint_url = "https://oauth.reddit.com/r/{}/api/info.json?id={}".format(subreddit,','.join(ids))
```

### Steps to run:

Each source has an independent schedule Python program that runs the collection program after a predefined schedule. This ensures isolation in case of any issues. In order to run the data collection system for the project, please find the below steps. Other than these, we need to run the faktory service and a one-time job queuing script to enqueue existing data.
1. Install the requirements, Note that some of the requirements need us to use Python virtual environments
   ```
   pip install -r requirements.txt
   ```
2. Modify the environment variables in the .env file ( you might need to create your own). 
```
touch .env
```
Add the values accordingly for these variables:
```
DATABASE_URL=
FAKTORY_URL=
MODERATEHATESPEECH_TOKEN=
```

4. Start the service
   ```
   nohup python3 -u faktory_service/services.py > {yyyymmdd}services.log &
   ```
5. Enqueue the existing data
   ```
   nohup python3 -u faktory_service/init_github.py > {yyyymmdd}init_github.log &
   nohup python3 -u faktory_service/init_reddit.py > {yyyymmdd}init_reddit.log &   
   ```
Once all the existing data have been enqueued, we run the next jobs. This is essential to ensure we don't insert two sentiments for the same record.

5. Github
   ```
   nohup python3 -u scheduleGithub.py > {yyyymmdd}github.log &
   ```

6. Reddit
   ```
   nohup python3 -u scheduleReddit.py > {yyyymmdd}reddit.log &
   ```

The above log files are related to the schedular program. For individual services, the logs are generated using <i>logging</i> package in the logs folder of the project.

### Design
![Data_Collection_ _Toxicity_Arch](https://github.com/2023-Fall-CS-415-515/project-2-implementation-ayadav7-arasal2/assets/113080362/0c0f49cb-76cf-4264-8949-568a7608315f)


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
- updateReddit.py: contains code to update the interaction data for existing Reddit records.

3. faktory_service:
This folder contains code for collecting sentiment data:
- config: files containing data related to token, config
- logs: stores the log
- SQL: DDLs for creating sentiment tables.
- moderatehatespeech: Code for making request to the api
- init_github.py: adding the existing data to queue
- init_reddit.py: adding the existing data to queue
- service.py: code to handle items in queues.
  
4. scheduleGithub.py

runs the different python programs to close issues, get new issues and get comments.

5. scheduleReddit.py
   
runs the reddit crawler every 60 seconds to get data.

6. backup.sh

creates a backup of data stored in <b>socialmedia</b> database

### Adding a new datasource to the toxicity service
In order to add new sources, we need to ensure meeting some requirements. One of them is sending the parameters, which are mentioned in the details above and another is table for storing the sentiments follow the naming convention.
Any data source you add, must have the sentiment table name as 'src_table_sentiment' as its name.
For example:
if 'twitter_data' is the source table, then we will have to create a sentiment table as 'twitter_data_sentiment'. Furthermore, the foreign key to link to the original source must have same name as the original source. 

