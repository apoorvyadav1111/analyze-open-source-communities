import streamlit as st
from wordcloud import WordCloud, STOPWORDS
from utils import run_query, get_subreddits
from streamlit_javascript import st_javascript
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.set_option('deprecation.showPyplotGlobalUse', False)


def get_color():
    return_value = st_javascript("""function darkMode(i){return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)}(1)""")
    color = 'white' if return_value == 0 else (14, 17, 23)
    border_color = 'white' if return_value == 0 else (14/255, 17/255, 23/255)
    return color, border_color

def get_word_cloud(start_date, end_date, subreddit, color):
    if subreddit == "all":
        query = f"""
            SELECT
                body
            FROM
                reddit_comments
            inner join
            (
            SELECT

                comment_id
            FROM
                reddit_comments_sentiment
            WHERE
                class != 'normal'
            )sentiment
            on reddit_comments.comment_id = sentiment.comment_id
            WHERE
                inserted_at between '{start_date}' and '{end_date}' and subreddit != 'politics';
            """
    else:
        query = f"""
            SELECT
                body
            FROM
                reddit_comments
            inner join
            (
            SELECT
                comment_id
            FROM
                reddit_comments_sentiment
            WHERE
                class != 'normal'
            )sentiment
            on reddit_comments.comment_id = sentiment.comment_id
            WHERE
                subreddit = '{subreddit}'
            and inserted_at between '{start_date}' and '{end_date}';
        """

    data = run_query(query)
    
    # Create a DataFrame from the query result
    text = "".join([row[0] for row in data])
    if not text:
        st.warning("No Data Found")
        return None
    text = text.lower()
    stop_words = set(STOPWORDS) 
    final_wordcloud = WordCloud(
                                background_color=color, 
                                stopwords=stop_words, 
                                min_font_size=4).generate(text)     
    return final_wordcloud

def get_subreddit_toxicity(start_date, end_date):
    query = f"""
        select 
            count(*) as comment_count, 
            subreddit
            from reddit_comments 
        where 
        created_utc BETWEEN '{start_date}' AND '{end_date}'   and subreddit != 'politics'
        and
        comment_id in 
        (
            select 
                comment_id 
            from 
                reddit_comments_sentiment 
            where 
            class != 'normal'
        ) 
        group by subreddit
        order by count(*);
        """
    data = run_query(query)
    return data

def parse_data(data):
    if not data:
        return [
            {
                "Subreddit": "No Data",
                "Records": 0
            }
        ]
    return [
        {
            "Subreddit": row[1],
            "Records": row[0]
        }
        for row in data
    ]

def show_toxic_comments(start_date, end_date, subreddit):
    c0, c1 = st.columns(2)
    with c0:
        st.subheader("Toxic Comments")
    with c1:
        choice = st.radio("Show data for:", ["7 days", "Selected Range"], index=0)
    if choice == "Selected Range":
        where_clause = f" and inserted_at BETWEEN '{start_date}' AND '{end_date}'"
    else:
        where_clause = f" and inserted_at > CURRENT_TIMESTAMP - INTERVAL '7 days'"
    query =f"""
        SELECT
            body,
            concat('r/',subreddit),
            created_utc
        FROM
            reddit_comments
        inner join
        (
        SELECT
            comment_id
        FROM
            reddit_comments_sentiment
        WHERE
            class != 'normal'
            {where_clause}
        )sentiment
        on reddit_comments.comment_id = sentiment.comment_id
        """
    if subreddit != "all":
        query += f"WHERE reddit_comments.subreddit = '{subreddit}' order by created_utc desc ;"
    else:
        query += "  where subreddit != 'politics' order by created_utc desc;"
    data = run_query(query)
    st.dataframe(data,column_config={
        "0": "Comment",
        "1": "Subreddit",
        "2": "Created Date"}, use_container_width=True)

def toxic_comments_timeline(start_date, end_date, subreddit):
    query = f"""
        SELECT
            date_trunc('day',inserted_at) as day,
            count(*)
        FROM
            reddit_comments
        inner join
        (
        SELECT
            comment_id
        FROM
            reddit_comments_sentiment
        WHERE
            class != 'normal'
            and inserted_at between '{start_date}' and '{end_date}'
        )sentiment
        on reddit_comments.comment_id = sentiment.comment_id
        """
    if subreddit != "all":
        query += f"WHERE reddit_comments.subreddit = '{subreddit}' group by day;"
    else:
        query += "group by day;"

    
    data = run_query(query)
    data = [
        {
            "Date": row[0],
            "Toxic Comments": row[1]
        }
        for row in data
    ]
    st.subheader("       \tToxic Comments in {}".format(subreddit))
    st.line_chart(data, x="Date", y="Toxic Comments")



st.header("Open Source Projects Community Dashboard: Toxicity on Reddit")
col0, col1, col2 = st.columns(3)
with col0:
    subreddit = st.selectbox("Subreddit", ["all"] + [row[0] for row in get_subreddits()])
with col1:
    start_date = st.date_input("Start Date", datetime.now()-timedelta(days=30))
with col2:
    end_date = st.date_input("End Date", datetime.now())

col1, col2 = st.columns(2)
with col1:
    # subreddit = st.selectbox("Subreddit", ["all"] + [row[0] for row in get_subreddits()])
    fig_word_cloud = None
    color, border_color = get_color()
    fig_word_cloud = get_word_cloud(start_date, end_date, subreddit, color)
    plt.gcf().set_facecolor(border_color)
    try:
        plt.imshow(fig_word_cloud, interpolation='bilinear')
        plt.axis('off')
        # plt.savefig("wordcloud.pdf", facecolor=border_color, bbox_inches='tight')
        plt.show()
        st.pyplot()
    except Exception as e:
        st.error("Cannot Generate a Word Cloud, Please try again/ refresh the page")


with col2:
    if subreddit == "all":
        st.subheader("Toxicity per Subreddit")
        data = get_subreddit_toxicity(start_date, end_date)
        data = parse_data(data)
        st.bar_chart(data,x="Subreddit",y="Records", color="Subreddit")
    else:
        toxic_comments_timeline(start_date, end_date, subreddit)
    

def get_comments_count_per_author(start_date, end_date, subreddit):
    where_clause = f"subreddit != 'politics' and created_utc BETWEEN '{start_date}' AND '{end_date}'" 
    if subreddit != "all":
        where_clause += f" and subreddit = '{subreddit}'"
    
    query = f"""
        select
            comment_count as frequency,
            count(*) as counts
        from
            (
            select 
                count(*) as comment_count, 
                author
                from reddit_comments 
            where 
            {where_clause}
            and
            comment_id in 
            (
                select 
                    comment_id 
                from 
                    reddit_comments_sentiment 
                where 
                class != 'normal'
            ) 
            group by author
            order by count(*)
            )a
        group by a.comment_count;
        """

    data = run_query(query)
    x = "Count of toxic comments per user"
    y = "Number of users"
    if not data:
        data = [
            {
                x: 0,
                y: 0
            }
        ]
    else:
        data = [
            {
                x: row[0],
                y: row[1]
            }
            for row in data
        ]
    
    st.subheader("Repeated Toxic Comments in {} subreddit".format(subreddit))
    st.bar_chart(data, x=x, y=y, color="#ff0000")


st.markdown("---")
c1, c2 = st.columns([5,2], gap='medium')
with c1:
    show_toxic_comments(start_date, end_date, subreddit)
with c2:
    get_comments_count_per_author(start_date, end_date, subreddit)

st.markdown("---")
help_text = """
This page shows the toxicity of the comments on Reddit for the selected date range.
The word cloud shows the most used words in the comments.
The bar chart shows the number of toxic comments per subreddit.
When a subreddit is selected, the line chart shows the number of toxic comments per day.
The table shows the toxic comments in the last 7 days.
"""
st.info(help_text, icon="ℹ️")