-- migrate:up
CREATE TABLE categories (
    category_id CHAR NOT NULL PRIMARY KEY,
    alternate_name VARCHAR(64),
    color VARCHAR(7),
    min_points INT NOT NULL DEFAULT 0,
    max_points INT NOT NULL DEFAULT 4000,
    start_time TIMESTAMP NOT NULL,
    women_only BOOL NOT NULL DEFAULT FALSE,
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
    club VARCHAR(255) NOT NULL,
    total_actual_paid INT NOT NULL DEFAULT 0
);

CREATE TABLE entries (
    category_id CHAR NOT NULL,
    licence_no INT NOT NULL,
    color VARCHAR(7),
    registration_time TIMESTAMP NOT NULL DEFAULT NOW(),
    marked_as_paid BOOL NOT NULL DEFAULT FALSE,
    marked_as_present BOOL NOT NULL DEFAULT FALSE,
    PRIMARY KEY (category_id, licence_no),
    UNIQUE (color, licence_no),
    FOREIGN KEY (category_id)
    REFERENCES categories (category_id) ON DELETE RESTRICT,
    FOREIGN KEY (licence_no)
    REFERENCES players (licence_no) ON DELETE CASCADE
);

-- migrate:down
DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS categories;
