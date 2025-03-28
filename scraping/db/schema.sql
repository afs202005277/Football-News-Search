DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS team_info;
DROP TABLE IF EXISTS game_report;

CREATE TABLE article(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    publish_date DATE NOT NULL,
    origin TEXT NOT NULL
);

CREATE TABLE team_info(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE game_report(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    home TEXT NOT NULL,
    away TEXT NOT NULL,
    result TEXT NOT NULL,
    date DATETIME NOT NULL,
    content TEXT NOT NULL,
    home_goals INT NOT NULL,
    away_goals INT NOT NULL
);