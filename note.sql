create database FastAPI_notebook;
use FastAPI_notebook;
CREATE TABLE users (
    id int unsigned auto_increment primary key,
    username varchar(50) unique not null,
    password varchar(255) not null,
    email varchar(100) unique,
    full_name varchar(100),
    created_at timestamp default current_timestamp
);

create table notes(
	id bigint unsigned auto_increment primary key,
    user_id int unsigned not null,
    title varchar(100),
    content text,
    created_time datetime not null default current_timestamp,
    updated_time datetime not null default current_timestamp on update current_timestamp,
    foreign key (user_id) references users(id)
);

create table tags(
	id bigint unsigned auto_increment primary key,
    tag_name varchar(50) unique not null
);

create table note_tag(
	note_id bigint unsigned not null,
    tag_id bigint unsigned not null,
    primary key (note_id, tag_id),
    foreign key (note_id) references notes(id) on delete cascade,
    foreign key (tag_id) references tags(id) on delete cascade
);

select * from users;
select * from notes;
select * from tags;
select * from note_tag;

