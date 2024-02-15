CREATE TABLE github_issues_sentiment (
    id SERIAL PRIMARY KEY,
    issue_number VARCHAR(255),
    class VARCHAR(255),
    confidence FLOAT,
    inserted_at TIMESTAMP DEFAULT NOW()
);