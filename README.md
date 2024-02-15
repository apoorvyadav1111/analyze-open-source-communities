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
![image](https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/1259d706-1888-4cdd-97f3-afc69b011ae8)



## Running Dashboard Screenshots
1. Home page
<img width="1360" alt="image" src="https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/7162f9e2-c858-4882-a877-f0bbaae1c189">


2. Data Overview page
<img width="1372" alt="image" src="https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/b2f3765d-7f68-40f3-98c6-5221e98e0e51">
<img width="1388" alt="image" src="https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/ea1119b0-0522-4fb8-990b-4c94aeb4a30a">



3. Live Data page
<img width="1359" alt="image" src="https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/e4dabf1d-470e-4ff8-ae81-dbea6b401051">


4. Toxicity page
<img width="1375" alt="image" src="https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/a91268f9-a5b5-40fe-851d-75f24b1ce753">
<img width="1332" alt="image" src="https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/dcb424af-c1f3-44ad-9f72-ffbea0182daf">

5. Activity page
<img width="1351" alt="image" src="https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/bf71aa86-105c-4522-b7f2-503e8498e08b">

6. About page
<img width="1390" alt="image" src="https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/8c6a13d8-5b8b-4fa8-a1f9-244de22538af">
<img width="1384" alt="image" src="https://github.com/apoorvyadav1111/analyze-open-source-communities/assets/32174554/f6a2e895-744a-4429-b3b8-51d0e8ffc2c8">


## References
* [Streamlit](https://www.streamlit.io/)
* [Postgres](https://www.postgresql.org/)
* [Faktory](https://contribsys.com/faktory/)
* [Moderate Hate Speech](https://www.moderatehatespeech.com/)
* [Matplotlib](https://matplotlib.org/)
* [Python](https://www.python.org/)


