create database testdb;

\c testdb

create table student(name varchar(20), age int);



INSERT INTO student (name, age) VALUES ('Alice', 30);
INSERT INTO student (name, age) VALUES ('Bob', 40);

select * from student;


begin;


UPDATE student SET age = 31 WHERE name = 'Alice';

DELETE FROM student WHERE name = 'Bob';


rollback;


drop database testdb;


