CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time_stamp TEXT NOT NULL,
    title TEXT NOT NULL,
    msg TEXT NOT NULL,
    'level' INTEGER NOT NULL
);