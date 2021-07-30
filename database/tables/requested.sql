set search_path to hsrr,public;

create table if not exists hsrr.requested(
sec varchar references network(sec),
reversed bool,
xsp varchar,
coverage float,
note varchar,
pk serial primary key,
UNIQUE (sec,reversed,xsp)
);