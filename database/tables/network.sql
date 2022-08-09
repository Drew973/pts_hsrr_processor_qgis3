
create table if not exists hsrr.network
    (
    sec text primary key
	,id serial--needed for pgRouting to make topology.
	,geom geometry('linestring',27700)
	,meas_len float
	,buffer geometry('polygon',27700)
	,has_forward bool
	,has_reverse bool
	,funct varchar--slip road,main carriageway...use to filter?
    );


insert into hsrr.network(sec) values ('D') on CONFLICT DO NOTHING;
create index if not exists buffer_index on hsrr.network using gist(buffer);
create index if not exists geom_index on hsrr.network using gist(geom);