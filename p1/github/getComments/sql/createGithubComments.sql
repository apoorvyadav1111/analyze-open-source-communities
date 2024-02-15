CREATE TABLE github_comments (
    id SERIAL PRIMARY KEY,
    issue_id INT,
    comment_id INT,
    user_id INT,
    created_at TIMESTAMP,
    body TEXT,
    reaction_plus_1 INT,
    reaction_minus_1 INT,
    reaction_laugh INT,
    reaction_hooray INT,
    reaction_confused INT,
    reaction_heart INT,
    reaction_rocket INT,
    reaction_eyes INT,
    inserted_at TIMESTAMP,
    repo_name VARCHAR(255)
);
