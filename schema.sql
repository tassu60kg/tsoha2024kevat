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

CREATE TABLE cliques (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    clique TEXT
);

CREATE TABLE clique_score (
    id SERIAL PRIMARY KEY,
    clique TEXT,
    score INTEGER

);