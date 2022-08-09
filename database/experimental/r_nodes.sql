
drop table if exists hsrr.r_nodes;

create table if not exists hsrr.r_nodes 
(
	pk serial primary key
	,topo_pt geometry('point',27700)
	,run_pt geometry('point',27700)
	,run_ch float
	,topo_pk bigint
);