# Analytical Approach in Making Technical Stack Selection

## Abstract
Social Media is an integral part of our lives. 
It is omnipresent and influences our day-to-day decisions. 
We can collect a lot of this data and perform analysis on it. 
Using this data, we can gain insights on various situations. Web repository platforms are easy to use and manage open-source projects. 
Posting issues and getting them resolved is a part and parcel of open-source projects. 
On the other hand, for development related issues, support, any interesting findings and geeky discussions, users use social media platforms. We are collecting data from two sources, Reddit and GitHub. 
We used third party api, moderatehatespeech.com to predict toxicity of the records. Together, all the data will be used to explore the engagement and overall friendliness of the online communities.  This can facilitate users while making decision to choose any technology stack. We will further this by creating an interactive dashboard to facilitate users with our findings. We propose using Streamlit, an open-source Python library that makes it easy to create and share beautiful, custom web apps for machine learning and data science. 


## Team
* Akash Rasal
* Apoorv Yadav

## Tools used
* `python` - The project is developed and tested using python. [Python Website](https://www.python.org/)
* `streamlit` - The project is developed using streamlit as the backend. [Streamlit Website](https://www.streamlit.io/)
Additionally, while developing the project 1 and 2, we used the following tools:
* `postgres` - The primary database used for the project. [Postgres Website](https://www.postgresql.org/)
* `faktory` - The primary job queue used for the project 2. [Faktory Website](https://contribsys.com/faktory/)
* `moderatehatespeech` - The primary api used for the project 2. [Moderate Hate Speech Website](https://www.moderatehatespeech.com/)
* `matplotlib` - The primary plotting library used for the project. [Matplotlib Website](https://matplotlib.org/)


## Running this dashboard
<b> ;tldr: need to run project 2 to have live data page working, for all other charts, restoring database is more than enough </b>

[ Entire System ]
In order to get it completely running, we need to run the project 2 first. The project 2 is a data pipeline that collects data from various sources along with the toxicity and stores it in the database. It is an upgrade to project 1 where you only stored the data. The steps to get the project 2 running are listed in the project 2 [readme](https://github.com/2023-Fall-CS-415-515/project-2-implementation-ayadav7-arasal2). The prerequisite of running the project is the sytem should have postgres installed and running. Since, the steps can change with time, they can be found [here](https://www.postgresql.org/download/). 

[ restore database ]
On the other hand, if only dashboard needs to be run, we have provided the data in the `data` folder. The data is collected from the project2. The only caveat is that the live data page will not be updating since the data is static. The steps to run the dashboard are listed below:

1. Create a virtual environment
```
python3 -m venv dashboardenv
```
2. Activate the virtual environment ( below command for linux & mac)
```
source dashboardenv/bin/activate
```
3. Clone the repository and Change working directory
```
git clone git@github.com:2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2.git
cd project-3-implementation-ayadav7-arasal2 
```
4. Install the requirements
```
pip install -r requirements.txt
```
5. Restore the database using `pg_restore` command. The documentation to restore can be found [here](https://www.postgresql.org/docs/current/app-pgrestore.html). Since the parameters can change the below command is just provided as an example. The command requires an existing db in postgres. We can create one in postgres cli using  `create database <db_name>;`
```
pg_restore -h localhost -p 5432 -U postgres -d <db_name> -v <backup>
```
6. Create a `.env` file in the root directory and add the following lines to it, ensure that you keep the db_name same as what you restored into:
```
DATABASE_URL=postgres://postgres:<ur_password>@localhost:5432/<db_name>
```
7. Run the dashboard
```
streamlit run app.py
```
or to not send usage stats to streamlit
```
streamlit run app.py --browser.gatherUsageStats False
```

8. Open the browser and go to the url `http://localhost:8501/` or the one shown on terminal as `Network URL: http://<ip>:8501`


## Project Structure
* `app.py` - The main file that runs the dashboard and displays home page.
* `data` - The folder that contains the data for the dashboard. To restore it, we need postgres and pg_restore. It requires the postgres 16 for it to work.
* `live_data.py` - The file that contains the code for the live data page. The page updates every 5 minutes automatically. 
* `all_data.py` - The file that contains the code for the data overview page. The user can check overall data collection overtime for both reddit and github.
* `toxicity.py` - The file that contains the code for the toxicity page. User can select date range and a particular subreddit for a detailed view.
* `about.py` - The file that contains the code for the about page.
* `utils.py` - The file that contains the utility functions for the dashboard.
* `connect_to_db.py` - The file that contains the code to connect to the database.
* `requirements.txt` - The file that contains the dependencies for the dashboard.

## System Architecture
![image](https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/9e2f512d-5767-41c7-b228-5c34b8fd72bd)


## Running Dashboard Screenshots
1. Home page
<img width="1360" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/ec5c7424-6131-4a5d-823a-61eda4457941">


2. Data Overview page
<img width="1372" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/c4751ece-b37a-4633-8ac5-33e303a036f4">
<img width="1388" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/71e76250-ac38-4bb8-9215-e5b404fb0f90">



3. Live Data page
<img width="1359" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/ffe9dd84-8515-4100-9057-85d61a41497b">


4. Toxicity page
<img width="1375" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/8c53af6e-af3f-4991-aa51-50a5b3522e4a">
<img width="1332" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/3947b917-690c-4850-8cc8-50a87998cfda">


5. Activity page
<img width="1351" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/3b842f9a-c03a-460e-a047-237d0611d587">

6. About page
<img width="1390" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/80ca809d-f289-4a41-81ca-3480e6041b1f">
<img width="1384" alt="image" src="https://github.com/2023-Fall-CS-415-515/project-3-implementation-ayadav7-arasal2/assets/113153292/ee9bdd82-00a6-467b-a1fe-c7d0c2cc00a9">


## References
* [Streamlit](https://www.streamlit.io/)
* [Postgres](https://www.postgresql.org/)
* [Faktory](https://contribsys.com/faktory/)
* [Moderate Hate Speech](https://www.moderatehatespeech.com/)
* [Matplotlib](https://matplotlib.org/)
* [Python](https://www.python.org/)


