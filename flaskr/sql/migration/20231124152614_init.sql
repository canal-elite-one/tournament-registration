-- migrate:up
CREATE TABLE categories (
    category_id CHAR NOT NULL PRIMARY KEY,
    color VARCHAR(7),
    min_points INT DEFAULT 0,
    max_points INT DEFAULT 4000,
    start_time TIMESTAMP NOT NULL,
    women_only BOOL DEFAULT FALSE,
    entry_fee INT NOT NULL,
    reward_first INT NOT NULL,
    reward_second INT NOT NULL,
    reward_semi INT NOT NULL,
    reward_quarter INT,
    max_players INT NOT NULL,
    overbooking_percentage INT NOT NULL DEFAULT 0
);

CREATE TABLE players (
    licence_no INT PRIMARY KEY NOT NULL,
    bib_no INT UNIQUE DEFAULT NULL,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    gender CHAR NOT NULL,
    nb_points INT NOT NULL,
    club VARCHAR(255) NOT NULL
);

CREATE TABLE entries (
    entry_id SERIAL NOT NULL PRIMARY KEY,
    category_id CHAR NOT NULL,
    licence_no INT NOT NULL,
    color VARCHAR(7),
    registration_time TIMESTAMP NOT NULL DEFAULT NOW(),
    paid BOOL DEFAULT FALSE,
    showed_up BOOL DEFAULT FALSE,
    UNIQUE (category_id, licence_no),
    UNIQUE (color, licence_no),
    FOREIGN KEY (category_id)
    REFERENCES categories (category_id),
    FOREIGN KEY (licence_no)
    REFERENCES players (licence_no)
);

-- migrate:down
DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS categories;
