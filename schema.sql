
DROP TABLE IF EXISTS books;

CREATE TABLE books (
    book_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    dewey_decimal TEXT NOT NULL,
    genre       TEXT NOT NULL,
    location    TEXT NOT NULL,
    checked_out INTEGER NOT NULL,
    restricted  INTEGER,
    description TEXT,
    requested   TEXT);

DROP TABLE IF EXISTS checkout;

CREATE TABLE checkout (
    checkout_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL,
    book_id         INTEGER NOT NULL,
    date_checked_out TEXT NOT NULL,
    return_date     TEXT NOT NULL,
    extensions      INTEGER,
    is_returned     INTEGER NOT NULL,
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
    ('example', 'author', '000.1', 'Information', 'Floor 3', 0, 0),

    ('example2', 'author', '000.1', 'Information', 'Floor 2', 0, 1),
    ('example3', 'author', '000.1', 'Information', 'Floor 3', 1, 0)

;

INSERT INTO users
VALUES
    ('test', 'pass', '2025-03-02', 0)

;

INSERT INTO checkout (user_id, book_id, date_checked_out, return_date, extensions, is_returned,is_late)
VALUES
    ('testing', 3, '2025-02-08', '2025-03-11', 0, 0,1),
    ('tester', 5678, '2025-01-01', '2025-02-02', 0, 0,0),
    ('tester', 3, '2025-02-20', '2025-03-09', 0, 0,0),
    ('tester', 3, '2025-02-20', '2025-03-20', 0, 1,0),
    ('test', 3, '2025-02-20', '2025-03-19', 0, 1,0)


;
UPDATE checkout SET return_date = '2025-03-09'
WHERE checkout_id = 5;

select * from books;
select * from checkout;
select* from users;