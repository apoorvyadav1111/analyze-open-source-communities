CREATE TABLE reddit_comments (
    id SERIAL PRIMARY KEY,
    comment_id VARCHAR(255),
    subreddit VARCHAR(255),
    post_name VARCHAR(255),
    body TEXT,
    ups INT,
    downs INT,
    score INT,
    over_18 BOOLEAN,
    author VARCHAR(255),
    author_fullname VARCHAR(255),
    created_utc TIMESTAMP,
    inserted_at TIMESTAMP
);