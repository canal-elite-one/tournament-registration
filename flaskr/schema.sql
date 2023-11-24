CREATE TABLE categories (
    tableaux_id CHAR NOT NULL PRIMARY KEY,
    color VARCHAR(7),
    min_points INT DEFAULT 0,
    max_points INT DEFAULT 4000,
    start_time TIMESTAMP NOT NULL,
    women_only BOOL DEFAULT FALSE,
    inscription_fee INT NOT NULL,
    reward_first INT NOT NULL,
    reward_second INT NOT NULL,
    reward_semi INT NOT NULL,
    reward_quarter INT DEFAULT 0,
    max_players INT NOT NULL,
    overbooking_percentage INT DEFAULT 0
    );

CREATE TABLE players (
    licence_no INT NOT NULL,
    first_name VARCHAR(32) NOT NULL,
    last_name VARCHAR(32) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(12) NOT NULL,
    gender CHAR,
    nb_points INT NOT NULL,
    club VARCHAR(255) NOT NULL,
    left_to_pay INT NOT NULL
    );

CREATE TABLE inscriptions (
    inscription_id serial NOT NULL PRIMARY KEY,
    tableaux_id INT NOT NULL,
    licence_no INT NOT NULL,
    inscription_time TIMESTAMP NOT NULL,
    paid BOOL DEFAULT FALSE,
    showed_up BOOL DEFAULT FALSE,
    FOREIGN KEY(tableaux_id)
        REFERENCES tableaux(tableaux_id),
    FOREIGN KEY(licence_no)
        REFERENCES players(licence_no)
    );