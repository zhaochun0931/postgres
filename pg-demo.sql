CREATE DATABASE testdb;
\c testdb

CREATE TABLE test_table ( id SERIAL PRIMARY KEY, name VARCHAR(50));


INSERT INTO test_table (name) VALUES ('xxx');
INSERT INTO test_table (name) VALUES ('yyy');


SELECT * FROM test_table;

drop database testdb;
