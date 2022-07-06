create table if not exists hsrr.route_edges
	(
	pk serial primary key
	,start_run_ch numeric
	,end_run_ch numeric
	,sec text default 'D'
	,start_sec_ch numeric default 0
	,end_sec_ch numeric default 0
	,source int
	,target int
	,cost float
	,sec_geom geometry('linestring',27700) default null
	,run_geom geometry('multiLineString',27700) default null
	);


create table if not exists hsrr.route_nodes
(
	pk serial primary key,
	run_ch numeric,
	pt geometry('Point',27700)
);

create index on hsrr.route_nodes using gist(pt);