CREATE DATABASE testdb;
\c testdb

CREATE TABLE t1 ( id SERIAL PRIMARY KEY, name VARCHAR(50));

INSERT INTO t1 (name) VALUES ('xxx');
INSERT INTO t1 (name) VALUES ('yyy');

SELECT * FROM t1;

drop database testdb;










CREATE TABLE my_table (id int PRIMARY KEY, name VARCHAR(50));

-- Example: Insert a lot of rows into a table
BEGIN;
INSERT INTO my_table (id, name) 
SELECT generate_series(1, 10), md5(random()::text);
COMMIT;



