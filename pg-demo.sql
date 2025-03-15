CREATE DATABASE testdb;
\c testdb

CREATE TABLE test_table ( id SERIAL PRIMARY KEY, name VARCHAR(50));


INSERT INTO test_table (name) VALUES ('xxx');
INSERT INTO test_table (name) VALUES ('yyy');


SELECT * FROM test_table;

drop database testdb;




CREATE TABLE my_table (id int PRIMARY KEY, name VARCHAR(50));

-- Example: Insert a lot of rows into a table
BEGIN;
INSERT INTO my_table (id, name) 
SELECT generate_series(1, 10), md5(random()::text);
COMMIT;



