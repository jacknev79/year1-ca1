
DROP TABLE IF EXISTS books;

CREATE TABLE books (
    book_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    dewey_decimal TEXT NOT NULL,
    genre       TEXT NOT NULL,
    location    TEXT NOT NULL,
    checked_out INTEGER NOT NULL,
    restricted  INTEGER);

DROP TABLE IF EXISTS checkout;

CREATE TABLE checkout (
    checkout_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL,
    book_id         INTEGER NOT NULL,
    date_checked_out TEXT NOT NULL,
    date_returned   TEXT,
    extensions      INTEGER,
    is_late         INTEGER);

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id         TEXT PRIMARY KEY,
    password        TEXT NOT NULL,
    date_registered TEXT,
    has_late_fees   INTEGER NOT NULL

);

INSERT INTO books (title, author, dewey_decimal, genre, location, checked_out, restricted)
VALUES
    ('example', 'author', '000.1', 'Information', 'Floor 3', 0, 0)

;

INSERT INTO users
VALUES
    ('test', 'pass', '2025-03-02', 0)

;

INSERT INTO checkout (user_id, book_id, date_checked_out, date_returned, extensions, is_late)
VALUES
    ('test', 5239, '2025-01-01', '2025-01-02', 0, 0),
    ('test1', 5239, '2025-02-01', '2025-02-02', 0, 0)


;

select * from books;