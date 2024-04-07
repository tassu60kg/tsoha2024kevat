CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT
);
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    score INTEGER,
    user_id INTEGER
);