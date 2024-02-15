CREATE TABLE reddit_posts (
    id SERIAL PRIMARY KEY,
    subreddit VARCHAR(255),
    post_id VARCHAR(255),
    post_name VARCHAR(255),
    title TEXT,
    selftext TEXT,
    ups INT,
    downs INT,
    score INT,
    upvote_ratio FLOAT,
    over_18 BOOLEAN,
    url VARCHAR(255),
    author VARCHAR(255),
    author_fullname VARCHAR(255),
    link_flair_text VARCHAR(255),
    created_utc TIMESTAMP,
    inserted_at TIMESTAMP
);