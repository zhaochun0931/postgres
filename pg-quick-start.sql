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








create table t2 (id int);

insert into t2 select * from generate_series(1,100);

create temp table t2_temp as select * from t2 where id >= 30;

drop table t2;






create table t3 as select * from generate_series(1,100000) as id(int);
drop table t3;




create table t4 (id int, name varchar(100));
insert into t4 values(generate_series(1,10),'name_' || generate_series(1,10));

# select * from t4;
 id |  name
----+---------
  1 | name_1
  2 | name_2
  3 | name_3
  4 | name_4
  5 | name_5
  6 | name_6
  7 | name_7
  8 | name_8
  9 | name_9
 10 | name_10
(10 rows)

#


