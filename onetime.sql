drop table if exists access;

CREATE TABLE access (
    id integer primary key autoincrement,
    userid integer not null references users (id),
    otp varchar(6) not null,
    otp_time datetime not null,
    valid boolean not null default false
);

drop table if exists users;

CREATE TABLE users (
    id integer primary key autoincrement,
    username varchar(32) not null,
    password varchar(32) not null,
    email varchar(128) not null,
    phone varchar(32) not null,
    locked boolean not null default false
);

drop table if exists otp;

create table otp (
    id integer primary key autoincrement,
    user_id integer not null references users (id),
    otp varchar(6) not null,
    otp_time datetime not null,
    valid boolean not null default false
);