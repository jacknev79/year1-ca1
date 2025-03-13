
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
    ('Napoleonic Uniforms vol 1', 'John R. Elting', '903.001', 'History', 'Floor 3', 0, 0),
    ('Napoleonic Uniforms vol 2', 'John R. Elting', '903.002', 'History', 'Floor 3', 0, 0),
    ('Fouche, the man Napoleon feared', 'Nils Forssell', '920.001', 'History', 'Floor 3', 0, 1),
    ('Wuthering Heights', 'Emily Bronte', '820.001', 'Gothic Literature', 'Floor 1', 0, 0),
    ('Life of Mirabeau', 'Tallentyre', '920.003', 'History', 'Floor 3', 0, 1),
    ('Crime and Punishment', 'Fyodor Dostoevsky', '890.001', 'Russian Literature', 'Floor 2', 0, 0),
    ('History of the fall and decline of the Roman Empire', 'Edward Gibbon', '900.001', 'History', 'Floor 3', 0, 0),
    ('War and Peace', 'Leo Tolstoy', '890.002', 'Russian Literature', 'Floor 2', 0, 0),
    ('Computing presuppositions in an incremental natural language processing system', 'Derek Bridge', '000.001', 'Computer Science', 'Floor 2', 1, 0)
;

INSERT INTO checkout (user_id, book_id, date_checked_out, return_date, extensions, is_returned,is_late)
VALUES
    ('tester', 9, '2025-02-20', '2025-03-09', 0, 0,0),
    ('tester', 1, '2025-02-20', '2025-03-20', 0, 1,0)
;

UPDATE checkout SET return_date = '2025-03-09'
WHERE checkout_id = 6;

select * from books;
select * from checkout;
select* from users;