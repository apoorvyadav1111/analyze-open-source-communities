import streamlit as st
from utils import run_query, get_subreddits, get_repos
from datetime import datetime, timedelta
from collections import defaultdict

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')


def get_reddit_data(start_date, end_date, subreddit):
    if subreddit == "all":
        query = """
            SELECT 
                COUNT(*) AS record_count,
                DATE_TRUNC('day', a.day) AS day,
                a.type
            FROM 
            (
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Comment' AS type
                FROM reddit_comments 
                WHERE inserted_at BETWEEN '{start_date}' AND '{end_date}'
                  and subreddit != 'politics'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Posts' AS type
                FROM reddit_posts 
                WHERE inserted_at BETWEEN '{start_date}' AND '{end_date}'  and subreddit != 'politics'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Total' AS type
                FROM reddit_comments
                WHERE inserted_at BETWEEN '{start_date}' AND '{end_date}'   and subreddit != 'politics'
                UNION ALL
                SELECT
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Total' AS type
                FROM reddit_posts
                WHERE inserted_at BETWEEN '{start_date}' AND '{end_date}'   and subreddit != 'politics'

            ) a
            GROUP BY day, type
            ORDER BY day;
            """.format(start_date=start_date, end_date=end_date)
    else:
        query = """
            SELECT 
                COUNT(*) AS record_count,
                DATE_TRUNC('day', a.day) AS day,
                a.type
            FROM 
            (
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Comments' AS type
                FROM reddit_comments 
                WHERE subreddit = '{subreddit}'
                AND inserted_at BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Posts' AS type
                FROM reddit_posts 
                WHERE subreddit = '{subreddit}'
                AND inserted_at BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Total' AS type
                FROM reddit_comments
                WHERE subreddit = '{subreddit}'
                AND inserted_at BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Total' AS type
                FROM reddit_posts
                WHERE subreddit = '{subreddit}'
                AND inserted_at BETWEEN '{start_date}' AND '{end_date}'

            ) a
            GROUP BY day, type
            ORDER BY day;
            """.format(subreddit=subreddit, start_date=start_date, end_date=end_date)
    
    return run_query(query, None)

def get_github_data(start_date, end_date, repo):
    if repo == "all":
        query = """
            SELECT 
                COUNT(*) AS record_count,
                DATE_TRUNC('day', a.day) AS day,
                a.type
            FROM 
            (
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day
                    , 'Comments' AS type
                FROM github_comments 
                WHERE inserted_at BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day
                    , 'Issues' AS type
                FROM github_issues 
                WHERE inserted_at BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day
                    , 'Total' AS type
                FROM github_issues
                WHERE inserted_at BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day
                    , 'Total' AS type
                FROM github_comments
                WHERE inserted_at BETWEEN '{start_date}' AND '{end_date}'
            ) a
            GROUP BY day, type
            ORDER BY day;
            """.format(start_date=start_date, end_date=end_date)
    else:
        query = """
            SELECT 
                COUNT(*) AS record_count,
                DATE_TRUNC('day', a.day) AS day,
                a.type
            FROM 
            (
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Comments' AS type
                FROM github_comments 
                WHERE repo_name = '{repo}'
                AND inserted_at BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Issues' AS type
                FROM github_issues 
                WHERE repo_name = '{repo}'
                AND inserted_at BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Total' AS type
                FROM github_issues
                WHERE repo_name = '{repo}'
                AND inserted_at BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 
                    DATE_TRUNC('day', inserted_at) AS day,
                    'Total' AS type
                FROM github_comments
                WHERE repo_name = '{repo}'
                AND inserted_at BETWEEN '{start_date}' AND '{end_date}'
            ) a
            GROUP BY day, type
            ORDER BY day;
            """.format(repo=repo, start_date=start_date, end_date=end_date)
    return run_query(query, None)


def reddits_post_tags(start_date, end_date, subreddit):
    subreddit_filter = f"and subreddit = '{subreddit}'" if subreddit != "all" else ""
    query = f"""
        select 
            link_flair_text,
            date_trunc('day', inserted_at) as day,
            count(*) as record_count
        from reddit_posts
        where (link_flair_text is not null or link_flair_text != '')
        and inserted_at between '{start_date}' and '{end_date}'
        and subreddit != 'politics'
        {subreddit_filter}
        group by link_flair_text, day
        order by record_count desc;
        """
    data = run_query(query)
    st.subheader("Reddit Posts per Tag")
    if not data:
        st.warning("Something went wrong. Please try again later.")
        return

    new_data = defaultdict(list)

    for row in data:
        new_data[row[1]].append([row[0], row[2]])
    
    normalized_tags = []

    for day, data in new_data.items():
        temp = {
            "Help": 0,
            "Discussion": 0,
            "Project": 0,
            "Article": 0,
            "Video": 0,
        }
        for tag, count in data:
            tag = tag.lower().strip()
            if "help" in tag or "question" in tag or "support" in tag or "newbie" in tag or "advice" in tag:
                temp["Help"] += count
            elif "discussion" in tag:
                temp["Discussion"] += count
            elif "project" in tag:
                temp["Project"] += count
            elif "article" in tag or "blog" in tag or "tutorial" in tag or "guide" in tag or "education" in tag:
                temp["Article"] += count
            elif "video" in tag:
                temp["Video"] += count
        for tag, count in temp.items():
            normalized_tags.append([day, tag, count])
    
    chart_data  = [
        {
            "Day": row[0],
            "Tag": row[1],
            "Count": row[2]
        }
        for row in normalized_tags
    ]
    st.line_chart(chart_data, x="Day", y="Count", color="Tag")

def unique_users_per_day_on_reddit(start_date, end_date, subreddit):
    subreddit_filter = f"and subreddit = '{subreddit}'" if subreddit != "all" else ""
    query = f"""
        select 
            count(distinct author) as users,
            subreddit,
            date_trunc('day', inserted_at) as day
        from 
        (
            select 
                author,
                subreddit,
                inserted_at
            from reddit_posts
            where inserted_at between '{start_date}' and '{end_date}'
            {subreddit_filter}
            and subreddit != 'politics'
            union all
            select
                author,
                subreddit,
                inserted_at
            from reddit_comments
            where inserted_at between '{start_date}' and '{end_date}'
            and subreddit != 'politics'
            {subreddit_filter}
        ) a
        group by day, subreddit
        order by day;
        """
    data = run_query(query)
    st.subheader("Unique User Engagement per Day on Reddit")
    if not data:
        st.warning("Something went wrong. Please try again later.")
        return
    data = [
        {
            "Day": row[2],
            "Users": row[0],
            "Subreddit": row[1]
        }
        for row in data
    ]
    st.line_chart(data, x="Day", y="Users", color="Subreddit")

def unique_users_per_day_on_github(start_date, end_date, repo):
    repo_filter = f"and repo_name = '{repo}'" if repo != "all" else ""
    query = f"""
        select
            count(distinct user_id) as users,
            repo_name,
            day
        from
        (
            select 
                user_id as user_id,
                repo_name,
                date_trunc('day', inserted_at) as day
            from github_comments
            where inserted_at between '{start_date}' and '{end_date}'
            {repo_filter}
            union all
            select
                posted_user_id as user_id,
                repo_name,
                date_trunc('day', inserted_at) as day
            from github_issues
            where inserted_at between '{start_date}' and '{end_date}'
            {repo_filter}
        )a
        group by day, repo_name
        order by day;
        """
    
    data = run_query(query)
    st.subheader("Unique User Engagement per Day on GitHub")
    if not data:
        st.warning("Something went wrong. Please try again later.")
        return
    data = [
        {
            "Day": row[2],
            "Users": row[0],
            "Repo": row[1]
        }
        for row in data
    ]
    st.line_chart(data, x="Day", y="Users", color="Repo")

def parse_data(data):
    if not data:
        return [
            {
                "Time": datetime.now(),
                "Records": 0,
                "Type": "No Data"
            }
        ]
    return [
        {
            "Time": row[1],
            "Records": row[0],
            "Type": row[2]
        }
        for row in data
    ]
with st.container():
    st.header("Open Source Projects Community Dashboard: All Data")
    c1, c2 = st.columns(2)
    with c1:
        start_date = st.date_input("Start Date", value=datetime.now()-timedelta(days=7), min_value=None, max_value=None, key=None)
    with c2:
        end_date = st.date_input("End Date", value=datetime.now(), min_value=None, max_value=None, key=None)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("## Reddit")
        subreddit = st.selectbox("Subreddit", ["all"] + [row[0] for row in get_subreddits()])
        data = get_reddit_data(start_date, end_date, subreddit)
        st.line_chart(parse_data(data),x="Time",y="Records",color="Type")
    with c2:
        st.markdown("## Github")
        repo = st.selectbox("Repo", ["all"] + [row[0] for row in get_repos()])
        data = get_github_data(start_date, end_date,repo)
        st.line_chart(parse_data(data),x="Time",y="Records",color="Type")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        unique_users_per_day_on_reddit(start_date, end_date, subreddit)
    with c2:
        unique_users_per_day_on_github(start_date, end_date, repo)
    st.markdown("---")
    c1, c2 = st.columns([3,2])
    with c1:
        reddits_post_tags(start_date, end_date, subreddit)
    with c2:
        help_text = """
        This page shows the activity on the open source communities.
        The line chart shows the number of comments and posts on Reddit and the number of comments and issues on GitHub.
        Additionally, the chart shows the types of posts on Reddit per day.
        Please change the data range and the subreddit/repo to see the data for a specific time period and a specific subreddit/repo.
        """
        st.markdown("#")
        st.markdown("#")
        st.markdown("#")
        st.markdown("#")

        st.info(help_text, icon="ℹ️")

    


