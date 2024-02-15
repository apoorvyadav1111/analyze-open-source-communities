CREATE TABLE reddit_comments_sentiment (
    id SERIAL PRIMARY KEY,
    comment_id VARCHAR(255),
    class VARCHAR(255),
    confidence FLOAT,
    inserted_at TIMESTAMP DEFAULT NOW()
);