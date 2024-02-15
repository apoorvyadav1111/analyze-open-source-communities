CREATE TABLE github_issues (
    id SERIAL PRIMARY KEY,
    repo_name VARCHAR(255),
    issue_id BIGINT,
    issue_number INT,
    title TEXT,
    body TEXT,
    reactions_plus_1 INT,
    reactions_minus_1 INT,
    reaction_laugh INT,
    reaction_hooray INT,
    reaction_confused INT,
    reaction_heart INT,
    reaction_rocket INT,
    reaction_eyes INT,
    posted_user_id BIGINT,
    posted_user_username VARCHAR(255),
    labels JSONB,  -- Assuming labels are stored as JSONB data
    state VARCHAR(20),  -- Assuming state is one of 'open' or 'closed'
    assignee VARCHAR(255),  -- Assuming a single assignee as a username
    number_of_comments INT,
    created_dt TIMESTAMP,
    updated_at TIMESTAMP,
    closed_at TIMESTAMP,
    author_association VARCHAR(255),
    inserted_at TIMESTAMP
);
