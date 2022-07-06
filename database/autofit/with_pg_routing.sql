drop table if exists hsrr.edges;

create table if not exists hsrr.edges
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
);

delete from hsrr.edges;

insert into hsrr.edges(start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,cost)

select start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch
, hsrr.cost(run,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,run_geom)
from hsrr.get_edges('M62 SLIPS WB RE');



with a as (select generate_series(min(s_ch),max(e_ch),0.001) as start_run_ch,max(e_ch) from hsrr.readings where run='M62 SLIPS WB RE')
insert into hsrr.edges(start_run_ch,end_run_ch,cost)
select start_run_ch,least(start_run_ch+0.001,max) as end_run_ch,50
from a where start_run_ch+0.001<max;

select * from hsrr.edges order by start_run_ch desc;



drop table if exists hsrr.route_nodes;

create table if not exists hsrr.route_nodes
(
	pk serial primary key,
	run_ch numeric
);

delete from hsrr.route_nodes;

insert into hsrr.route_nodes(run_ch)
select distinct(start_run_ch) from hsrr.edges union
select distinct(end_run_ch) from hsrr.edges;


--select * from hsrr.route_nodes

update hsrr.edges set source = route_nodes.pk from hsrr.route_nodes where start_run_ch = route_nodes.run_ch;
update hsrr.edges set target = route_nodes.pk from hsrr.route_nodes where end_run_ch = route_nodes.run_ch;


--https://docs.pgrouting.org/1.x/en/dijkstra.html




create extension if not exists pgRouting;


--source and target need to be int
--id any int,source any int ,target any int,cost any numerical

select * from pgr_dijkstra('select pk as id, source, target, cost from hsrr.edges'
					,(select source from hsrr.edges order by start_run_ch limit 1)
					,(select target from hsrr.edges order by end_run_ch desc limit 1))
					
	inner join hsrr.edges on edges.pk = edge and sec!='D'