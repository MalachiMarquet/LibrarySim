

CREATE TABLE books (
    id                  SERIAL PRIMARY KEY,
    bookID              VARCHAR(50)     NOT NULL,
    title               VARCHAR(255)    NOT NULL,
    author              VARCHAR(1000)    NOT NULL,
    average_rating      NUMERIC(2, 1)  NOT NULL CHECK (average_rating >= 0.0 AND average_rating <= 5.0),
    isbn                INTEGER         NOT NULL,
    isbn13              CHAR(13)        NOT NULL,
    language_code       VARCHAR(10)    NOT NULL,
    num_pages           SMALLINT        NOT NULL CHECK (num_pages > 0),
    ratings_count       INTEGER         NOT NULL,
    text_review_count   INTEGER         NOT NULL,
    publication_date    DATE            NOT NULL,
    publisher           VARCHAR(255)    NOT NULL
);
    

CREATE TABLE employees (
    id          SERIAL PRIMARY KEY,
    first_name  VARCHAR(50)     NOT NULL,
    last_name   VARCHAR(50)     NOT NULL,
    email       VARCHAR(100)    UNIQUE NOT NULL,
    department  VARCHAR(50),
    salary      NUMERIC(10, 2),
    hire_date   DATE,
    is_active   BOOLEAN         DEFAULT TRUE,
    created_at  TIMESTAMPTZ     DEFAULT NOW()
);


CREATE TABLE customers (
    id          SERIAL PRIMARY KEY,
    first_name  VARCHAR(50)     NOT NULL,
    last_name   VARCHAR(50)     NOT NULL,
    email       VARCHAR(100)    UNIQUE NOT NULL,
    department  VARCHAR(50),
    salary      NUMERIC(10, 2),
    hire_date   DATE,
    is_active   BOOLEAN         DEFAULT TRUE,
    created_at  TIMESTAMPTZ     DEFAULT NOW()
);


COPY books (bookID, title, author, average_rating, isbn, isbn13, language_code, num_pages, ratings_count, text_review_count, publication_date, publisher        )
FROM 'C:/Coding/SQL/Library/books.csv'
WITH (FORMAT csv, HEADER);

