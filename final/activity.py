import streamlit as st
from datetime import datetime, timedelta
import collections

from utils import run_query

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

subreddit2cat = {
    "typescript":"Typescript",
    "NixOS":"Nix",
    "rust":"Rust",
    "FlutterDev":"Flutter",
    "golang":"Go",
    "kubernetes":"Kubernetes",
    "swift":"Swift"
}

repo2cat = {
    "NixOS_nixpkgs":"Nix",
    "flutter_flutter":"Flutter",
    "golang_go":"Go",
    "kubernetes_kubernetes":"Kubernetes",
    "rust-lang_rust":"Rust",
    "apple_swift":"Swift",
    "microsoft_TypeScript":"Typescript"
}


def parse_data(A,B,C, b,c):
    if not A:
        return [
            {
                "Community": "No Data",
                "Technology": "No Data",
                "Hours": 0
            }
        ]
    else:
        return [
            {
                "Community": b,
                "Technology": row[0],
                "Hours": row[1]
            }
            for row in zip(A,B)
        ] + [
            {
                "Community": c,
                "Technology": row[0],
                "Hours": row[1]
            }
            for row in zip(A,C)

        ]


def avg_response_time(start_date, end_date):
    query = """
        select 
        a.repo_name,
        a.issue_number,
        a.created_dt,
        b.created_at 
    from github_issues a 
    inner join 
    (
        select 
            c.issue_number,
            c.repo_name,
            c.comment_id,
            c.created_at from 
            (
                select 
                    issue_number, 
                    repo_name,
                    comment_id, 
                    created_at, 
                    rank() over (partition by repo_name, issue_number order by created_at asc) rank_number 
                from github_comments
            )c 
        where c.rank_number=1
    )b
    on a.issue_number=b.issue_number
    and a.repo_name = b.repo_name
    where a.created_dt between %s and %s;
    """

    values = (start_date, end_date)

    data = run_query(query, values)
    repos_data = collections.defaultdict(list)

    for row in data:
        if row[0] and row[1] and row[2] and row[3] :
            repos_data[repo2cat[row[0]]].append(((row[3] - row[2]).total_seconds() / 60)/60)


    query = """
        select 
        a.subreddit,
        a.post_name,
        a.created_utc,
        b.created_utc 
    from reddit_posts a 
    inner join 
    (
        select 
            c.post_name,
            c.subreddit,
            c.created_utc from 
            (
                select 
                    post_name, 
                    subreddit,
                    comment_id, 
                    created_utc, 
                    rank() over (partition by post_name order by created_utc asc) rank_number 
                from reddit_comments where subreddit!='politics'
            )c 
        where c.rank_number=1
    )b
    on a.post_name=b.post_name
    and a.subreddit = b.subreddit
    and a.subreddit!='politics'
    where a.created_utc between %s and %s;
    """
    data = run_query(query, values)
    if not data:
        st.warning("No data found for the selected date range")
        return [
            {
                "Community": "No Data",
                "Technology": "No Data",
                "Hours": 0
            }
        ]
    subreddit_data = collections.defaultdict(list)
    for row in data:
        if row[0] is not None and row[0] != 'politics' and row[1] is not None and row[2] is not None:
            subreddit_data[subreddit2cat[row[0]]].append(((row[3] - row[2]).total_seconds() / 60)/60)
    
    X = subreddit2cat.values()
    Y = []
    Z = []
    for x in X:
        Y.append(round(sum(repos_data[x]) / max(len(repos_data[x]),1),1))
        Z.append(round(sum(subreddit_data[x]) / max(len(subreddit_data[x]),1),1))
    
    data = parse_data(X,Y,Z, "GitHub", "Reddit")
    return data


def avg_resolution_time(start_date, end_date):
    query = """
        SELECT repo_name, issue_number, created_dt, closed_at FROM github_issues WHERE state = 'closed' AND closed_at IS NOT NULL and created_dt between %s and %s;
    """
    values = (start_date, end_date)
    data = run_query(query, values)

    if not data:
        st.warning("No data found for the selected date range")
        return [
            {
                "Community": "No Data",
                "Technology": "No Data",
                "Hours": 0
            }
        ]
    repos_data = collections.defaultdict(list)
    for row in data:
        if row[0] and row[1] and row[2] and row[3]:
            repos_data[repo2cat[row[0]]].append(((row[3] - row[2]).total_seconds() / 60) / 60)

    values1= []
    for k, v in repos_data.items():
        if v: 
            values1.append([k, sum(v) / len(v)])
    
    query = f"""
    select
        first.subreddit,
        first.post_name,
        last.created_utc-first.created_utc as active_time
    from
    (
        select 
        a.subreddit,
        a.post_name,
        b.created_utc 
    from reddit_posts a 
    inner join 
    (
        select 
            c.post_name,
            c.subreddit,
            c.created_utc from 
            (
                select 
                    post_name, 
                    subreddit,
                    comment_id, 
                    created_utc, 
                    rank() over (partition by post_name order by created_utc desc) rank_number 
                from reddit_comments where subreddit!='politics'
            )c 
        where c.rank_number=1
    )b
    on a.post_name=b.post_name
    and a.subreddit = b.subreddit
    and a.subreddit!='politics'
    ) last
    inner join
    (
        select 
        a.subreddit,
        a.post_name,
        b.created_utc 
    from reddit_posts a 
    inner join 
    (
        select 
            c.post_name,
            c.subreddit,
            c.created_utc from 
            (
                select 
                    post_name, 
                    subreddit,
                    comment_id, 
                    created_utc, 
                    rank() over (partition by post_name order by created_utc asc) rank_number 
                from reddit_comments where subreddit!='politics'
            )c 
        where c.rank_number=1
    )b
    on a.post_name=b.post_name
    and a.subreddit = b.subreddit
    and a.subreddit!='politics'
    )first
    on first.post_name=last.post_name
    and first.subreddit=last.subreddit
    WHERE
    first.created_utc BETWEEN '{start_date}' AND '{end_date}'
    ; 
    """   
    reddit_Data = run_query(query)

    subreddit_data = collections.defaultdict(list)

    for row in reddit_Data:
        if row[0] is not None and row[0] != 'politics' and row[1] is not None and row[2] is not None:
            subreddit_data[subreddit2cat[row[0]]].append(((row[2]).total_seconds() / 60) / 60)

    values2 = []
    for k, v in subreddit_data.items():
        if v:
            values2.append([k, sum(v)/len(v)])

    def parse(values1, values2, v1, v2):
        data = [

        ]
        for k,v in values1:
            data.append({
                "Technology": k,
                "Hours": round(v,1),
                "Community":v1
            })
        for k,v in values2:
            data.append({
                "Technology": k,
                "Hours": round(v,1),
                "Community":v2
            })
        return data
    data = parse(values1, values2, "GitHub", "Reddit")
    return data

st.header("Open Source Projects Community Dashboard: Activity")
c1, c2 = st.columns(2,gap='medium')
with c1:
    start_date = st.date_input("Start Date", datetime.now()-timedelta(days=7))
with c2:
    end_date = st.date_input("End Date", datetime.now())

c1, c2 = st.columns(2)
with c1:
    st.subheader("Average Time taken for first response")
    st.bar_chart(avg_response_time(start_date, end_date),y="Hours",x="Technology", color="Community")

with c2:
    st.subheader("Average Time taken in close issue/ last comment")
    st.bar_chart(avg_resolution_time(start_date, end_date),y="Hours",x="Technology", color="Community")

help_text = """
    This page shows the activity on open source communities. 
    The first bar chart shows the average time taken for the first response on GitHub and Reddit. First response is defined as the time between the issue creation and the first comment on GitHub and the time between the post creation and the first comment on Reddit.
    The second bar chart shows the average time taken to resolve an issue on GitHub and Reddit. Resolution time is defined as the time between the issue creation and the issue close on GitHub and the time between the post creation and the last comment on Reddit.
    Change the date range to see the activity for a different time period.
    """
st.info(help_text, icon="ℹ️")