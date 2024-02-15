import streamlit as st
from utils import run_query
import time
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

def get_live_data_reddit(freq):
    # SQL query
    trunc = 'minute' if freq == '1 hour' else 'hour'
    freq = '1 hours' if freq == '1 hour' else '1 days'
    query = f"""
        SELECT 
            COUNT(*) AS record_count,
            DATE_TRUNC('{trunc}', a.created_utc) AS minute,
            a.source AS source
        FROM 
        (
            SELECT 
                created_utc
                ,'Reddit Comments' as source
            FROM reddit_comments 
            where inserted_at > CURRENT_TIMESTAMP - INTERVAL '{freq}'
                and subreddit != 'politics'
            UNION ALL
            SELECT 
                created_utc
                ,'Reddit Posts' as source
            FROM reddit_posts
            WHERE inserted_at > CURRENT_TIMESTAMP - INTERVAL '{freq}'
                and subreddit != 'politics'
        ) a

        GROUP BY minute, source
        ORDER BY minute;
        """

    data = run_query(query)
    return data

def get_live_data_github(freq):
    # SQL query
    trunc = 'minute' if freq == '1 hour' else 'hour'
    freq = '1 hours' if freq == '1 hour' else '1 days'
    query = f"""
        SELECT 
            COUNT(*) AS record_count,
            DATE_TRUNC('{trunc}', a.created_dt) AS minute,
            a.source AS source
        FROM 
        (
            SELECT 
                created_at as created_dt,
                'Github Comments' as source
            FROM github_comments 
            where inserted_at > CURRENT_TIMESTAMP - INTERVAL '{freq}'
            UNION ALL
            SELECT 
                created_dt,
                'Github Issues' as source
            FROM github_issues
            WHERE inserted_at > CURRENT_TIMESTAMP - INTERVAL '{freq}'
        ) a
        GROUP BY minute, source
        ORDER BY minute;
        """

    data = run_query(query)
    return data 
 





# Plot the line charts in a two-column layout


def live_data(freq):
    col1, col2 = st.columns(2, gap='small')
    def update_data():
        data = get_live_data_reddit(freq)
        if not data:
            data1 = [
                {
                    "Count": 0,
                    "Time": 0,
                    "Source": "No Data"
                }
            ]
        else:
            data1 = [
                    {
                        "Count": row[0],
                        "Time": row[1],
                        "Source": row[2]
                    }
                    for row in data
                ]
        data = get_live_data_github(freq)
        if not data:
            data2 = [
                {
                    "Count": 0,
                    "Time": 0,
                    "Source": "No Data"
                }
            ]
        else:
            data2 = [
                {
                    "Count": row[0],
                    "Time": row[1],
                    "Source": row[2]
                }
                for row in data
                ]
        return data1, data2
    data1, data2 = update_data()
    with col1:
        st.markdown("## Reddit")
        st.line_chart(data1, x="Time", y="Count", color="Source")
    with col2:
        st.markdown("## Github")
        st.line_chart(data2, x="Time", y="Count", color="Source")
    help_text = """
    This page shows the live incoming data from the open source communities.
    It is refreshed every 5 minutes. Please select the frequency of the data you want to see.
    When you select 1 hour, the data is shown for the last hour, binned by minute. When you select 1 day, the data is shown for the last day binned hourly.
    """
    st.info(help_text, icon="ℹ️")


    time.sleep(5*60)
    
st.header("Open Source Projects Community Dashboard: Live Data")
freq = st.selectbox("Frequency", ["1 hour", "1 day"])
live_data(freq)
st.rerun()

