drop table if exists req cascade;
create table req(
	sec varchar references network(sec),
	reversed bool,
	xsp varchar,
	hmds varchar[],
	note varchar,
	primary key (sec,reversed,xsp)
);




