CREATE TABLE reddit_posts_sentiment (
    id SERIAL PRIMARY KEY,
    post_name VARCHAR(255),
    class VARCHAR(255),
    confidence FLOAT,
    inserted_at TIMESTAMP DEFAULT NOW()
);