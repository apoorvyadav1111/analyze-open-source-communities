import streamlit as st
from st_pages import Page, show_pages
from utils import run_query

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
# Hide Streamlit settings menu using CSS
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def home_summary():
    query = """
        select
            count(*) as total_issues
        from github_issues
    """
    total_issues = run_query(query)[0][0]
    query = """
        select
            count(*) as total_comments
        from github_comments
    """
    total_comments = run_query(query)[0][0]
    query = """
        select
            count(*) as total_submissions
        from reddit_posts
        where subreddit != 'politics'
    """
    total_submissions = run_query(query)[0][0]
    query = """
        select
            count(*) as total_comments
        from reddit_comments
        where subreddit != 'politics'
    """
    total_reddit_comments = run_query(query)[0][0]
    query = """
        select
            count(*) as count
        from reddit_comments_sentiment
        where class = 'flag'
    """
    total_toxic_comments = run_query(query)[0][0]
    query = """
        select
            count(*) as count
        from reddit_comments_sentiment
        where class = 'normal'
    """
    st.markdown("### Data Overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.success(f"Total Github Issues: {total_issues}") 
    with c2:
        st.success(f"Total Github Comments: {total_comments}")
    with c3:
        st.success(f"Total Reddit Submissions: {total_submissions}")
    with c4:
        st.success(f"Total Reddit Comments: {total_reddit_comments}")
    
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.error(f"Reddit Toxic Comments: {total_toxic_comments}")
    with c2:
        st.success(f"Reddit Normal Comments: {total_reddit_comments - total_toxic_comments}")

    st.markdown("---")


stack2subreddits = { 
    "Rust": "rust",
    "Go": "golang",
    "Nix": "NixOS",
    "Kubernetes": "kubernetes",
    "Swift": "swift",
    "Flutter": "FlutterDev",
    "TypeScript": "typescript",
}
stack2repo = {
    "Rust": "rust-lang_rust",
    "Go": "golang_go",
    "Nix": "NixOS_nixpkgs",
    "Kubernetes": "kubernetes_kubernetes",
    "Swift": "apple_swift",
    "Flutter": "flutter_flutter",
    "TypeScript": "microsoft_TypeScript",
}

def summarize_stack(stack):
    query1 = f"""
        select
            count(*) as total_issues,
            count(distinct posted_user_id) as distinct_users
        from github_issues
        where repo_name = '{stack2repo[stack]}'
    """
    query2 = f"""
        select
            count(*) as total_comments,
            count(distinct user_id) as distinct_users
        from github_comments
        where repo_name = '{stack2repo[stack]}'
    """

    query3 = f"""
        select
            count(*) as total_submissions,
            count(distinct author) as distinct_users
        from reddit_posts
        where subreddit = '{stack2subreddits[stack]}'
    """

    query4 = f"""
        select
            count(*) as total_comments,
            count(distinct author) as distinct_users
        from reddit_comments
        where subreddit = '{stack2subreddits[stack]}'
    """
    query5 = f"""
        select
            count(*) as count
        from reddit_comments_sentiment
        inner join reddit_comments on reddit_comments.comment_id = reddit_comments_sentiment.comment_id
        where reddit_comments.subreddit = '{stack2subreddits[stack]}' and reddit_comments_sentiment.class = 'flag'
    """
    query6 = f"""
        select
            count(*) as count
        from reddit_comments_sentiment
        inner join reddit_comments on reddit_comments.comment_id = reddit_comments_sentiment.comment_id
        where reddit_comments.subreddit = '{stack2subreddits[stack]}' and reddit_comments_sentiment.class = 'normal'

    """
    query7 = f"""
        select
            sum(ups) as total_upvotes,
            sum(downs) as total_downvotes
        from reddit_posts
        """
    query8 = f"""
        select
            sum(ups) as total_upvotes,
            sum(downs) as total_downvotes
        from reddit_comments
        """
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        total_issues, distinct_users = run_query(query1)[0]
        st.success(f"Total Github Issues: {total_issues}")
        st.success(f"Distinct Issue Users: {distinct_users}")
    with c2:
        total_comments, distinct_users = run_query(query2)[0]
        st.success(f"Total Github Comments: {total_comments}")
        st.success(f"Distinct Comment Users: {distinct_users}")
    with c3:
        total_submissions, distinct_users = run_query(query3)[0]
        st.success(f"Total Reddit Submissions: {total_submissions}")
        st.success(f"Distinct Submissions Users: {distinct_users}")
    with c4:
        total_comments, distinct_users = run_query(query4)[0]
        st.success(f"Total Reddit Comments: {total_comments}")
        st.success(f"Distinct Comments Users: {distinct_users}")
    
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        total_toxic_comments = run_query(query5)[0][0]
        st.error(f"Reddit Toxic Comments: {total_toxic_comments}")
    with c2:
        total_reddit_comments = run_query(query6)[0][0]
        st.success(f"Reddit Normal Comments: {total_reddit_comments - total_toxic_comments}")
    with c3:
        total_upvotes, total_downvotes = run_query(query7)[0]
        st.success(f"Reddit Post Upvotes: {total_upvotes}")
    with c4:
        total_upvotes, total_downvotes = run_query(query8)[0]
        st.success(f"Reddit Comment Upvotes: {total_upvotes}")
        

st.header("Open Source Projects Community Dashboard")
st.subheader("Welcome to the Open Source Projects Community Dashboard!")
st.markdown("---")
st.write("""This dashboard is a collection of data from the GitHub repositories of the most popular open source projects.
          The data is collected using the GitHub API and Reddit API is updated every hour. The data is then processed and visualized using Streamlit. 
         The dashboard is divided into 4 sections: Live Data, Toxicity Analysis, Activity & Response, and Data overview. 
         You can navigate between the sections using the sidebar on the left.""")

try:
    home_summary()
except Exception as e:
    st.warning("Could not get the summary. Please try again later.")

stack = st.selectbox(
    "Select a stack to view its summary",
    [
        "Rust",
        "Go",
        "Nix",
        "Kubernetes",
        "Swift",
        "Flutter",
        "TypeScript",
    ]
)
try:
    summarize_stack(stack)
except:
    st.warning("Could not get the summary for the selected stack. Please try again later.")

show_pages(
    [
        Page("./app.py", "Home"),
        Page("./all_data.py", "Data Overview"),
        Page("./live_data.py", "Live Data"),
        Page("./toxicity.py", "Toxicity Analysis"),
        Page("./activity.py", "Activity & Response"),
        Page("./info.py","About"),
    ]
)