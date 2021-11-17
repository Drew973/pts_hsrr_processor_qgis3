set search_path to hsrr,routes,topology,public;

drop view if exists network_edges cascade;

create view network_edges as 
select sec,False as reversed,start_node,end_node,edge_data.geom,edge_id 
from network_topo.edge_data where (select has_forward from network where network.sec=edge_data.sec)
union
select sec,True as reversed,end_node,start_node,st_reverse(edge_data.geom),edge_id 
from network_topo.edge_data where (select has_reverse from network where network.sec=edge_data.sec)
;


create table if not exists possible_edges
(
	pk int primary key
	,sec text
	,rev bool
	,start_node int
	,end_node int
	,cost numeric
	,edge_id int
	,start_chainage float
	,end_chainage float
	,geom geometry
);

/*
length_tol:geometry length within length_tol of chainage difference. in km.
cost of dummy=dummy_cost_per_length*chainage difference+min_dummy_cost

edges link where connected by toplogy edge.
dummys link where chanage difference < max_dummy_lengh
*/
CREATE OR REPLACE FUNCTION calculate_possible_edges(rn text,length_tol float=0.5,max_dummy_length float=3,dummy_cost_per_length float=2000,min_dummy_cost float=1000)
RETURNS void AS $$
	delete from hsrr.possible_edges;
	
	insert into possible_edges(pk,sec,rev,start_node,end_node,cost,edge_id,geom,start_chainage,end_chainage)

	select row_number() over (order by sec),sec,reversed,start_node,end_node,cost,edge_id,geom,start_chainage,end_chainage from
	(
	select sec,reversed,a.pk as start_node,b.pk as end_node,
	(select avg(st_distance(vect,geom)) from readings where run = rn and e_ch>=a.ch and s_ch<=b.ch) as cost
	,edge_id,geom,a.ch as start_chainage,b.ch as end_chainage
	from possible_changes a inner join network_edges on network_edges.start_node=a.node_id
	inner join possible_changes b on network_edges.end_node=b.node_id and a.ch<=b.ch and a.pk!=b.pk and b.ch-a.ch<length_tol+st_length(geom)/1000

	union

	select '',False,a.pk,b.pk,min_dummy_cost+(b.ch-a.ch)*dummy_cost_per_length as cost,null,st_makeLine(a.pt,b.pt),a.ch,b.ch
	from possible_changes a inner join possible_changes b on b.ch>=a.ch and b.pk!=a.pk and b.ch-a.ch<max_dummy_length
	)a
$$ LANGUAGE sql
SET search_path = hsrr,public
;




