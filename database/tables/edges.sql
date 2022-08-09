create table if not exists hsrr.route_edges
	(
	pk serial primary key
	,start_run_ch numeric(9,3)
	,end_run_ch numeric(9,3)
	,run_geometry geometry--only used for viewing/debugging.
	,sec text default 'D'
	,start_sec_ch numeric(9,3)  default 0
	,end_sec_ch numeric(9,3)  default 0
	--,sec_geom geometry('linestring',27700)
	,source bigint
	,target bigint
	,cost float
	);





create table if not exists hsrr.route_nodes
(
	pk serial primary key
	,run_ch numeric(9,3)--chainages can be repeated because gaps
	,pt geometry('point',27700) unique--points should not be repeated. snap to grid to compare.
);

create index on hsrr.route_nodes using gist(pt);