drop table if exists hsrr.r_edges;

create table hsrr.r_edges
(
	pk serial
	,source bigint
	,target bigint
	,run_geom geometry
	,topo_geom geometry
	,cost float
	,sec_id bigint
);
