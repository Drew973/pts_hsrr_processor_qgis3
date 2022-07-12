
/*
table of every requested section.direction/xsp.
used to view coverage.
*/


create table if not exists hsrr.requested(
sec varchar references hsrr.network(sec),
reversed bool,
xsp varchar,
coverage float,
note varchar,
pk serial primary key,
UNIQUE (sec,reversed,xsp)
);