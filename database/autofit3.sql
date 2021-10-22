create table if not exists possible_changes
(ch float
,node_id int
,pt geometry
,pk int primary key);



create table if not exists route_edges
(
	pk int primary key
	,sec text
	,rev bool
	,start_node int
	,end_node int
	,cost numeric
	,edge_id int
	,geom geometry
);

/*
possible changes is nodes of graph.
node_id is id of topology node. ie physical location.

connect each row to end of topology edge starting at node
and chainage near geometry length

and to all following rows through dummy


*/



/*
metric for how bad fit is.
geom = geometry of section.
*/



CREATE OR REPLACE FUNCTION cost(rn text,s float,e float,geom geometry)
RETURNS float AS $$
	select avg(st_distance(vect,geom)) from readings where run=rn and s_ch<e and e_ch>s;
$$ LANGUAGE sql immutable;




delete from possible_changes;

--possible changes of section
with a as (select s_ch,e_ch,vect,lead(vect) over (order by s_ch),lag(vect) over(order by s_ch) from readings where run = 'SEW NB CL1')
--nearby nodes

,b as (
select st_linelocatePoint(vect,geom)+s_ch as ch,node_id,geom as pt from network_topo.node inner join readings on run='SEW NB CL1' and st_dwithin(vect,geom,50)
union
--gaps+start+end
select e_ch,null as node_id,st_endPoint(vect) as pt from a where lead is null or not st_dwithin(vect,lead,100)
union
select s_ch,null,st_startPoint(vect) from a where lag is null or not st_dwithin(vect,lag,100)
)
insert into possible_changes(pk,ch,node_id,pt)
select row_number() over (order by ch),ch,node_id,pt from b;



delete from route_edges;

with 
c as (select pk,ch,start_node as topo_start_node,end_node as topo_end_node,edge_id,geom from possible_changes inner join network_topo.edge on start_node=node_id)
,e as (
--dummy to all following rows
select a.pk as start_node,b.pk as end_node,(b.ch-a.ch)*500 as cost,null as edge_id,st_makeLine(a.pt,b.pt) as geom from possible_changes as a inner join possible_changes as b 
on b.ch>a.ch 
union
--connected nodes within 100m of geom length
select c.pk as start_node,d.pk as end_node,cost('SEW NB CL1',c.ch,d.ch,geom),edge_id,geom from c inner join possible_changes as d on c.ch<d.ch and topo_end_node = node_id and d.ch-c.ch<st_length(geom)+100
)
--only want lowest cost edge
insert into route_edges(pk,start_node,end_node,cost,edge_id,geom)
SELECT DISTINCT ON (start_node,end_node) row_number() over (order by start_node),start_node, end_node, cost, edge_id,geom FROM e ORDER BY start_node,end_node,cost;

insert into routes.edge(start_node,end_node,cost,pk)
select start_node,end_node,cost,pk from route_edges;


update route_edges set sec = network.sec from network_topo.relation inner join network on relation.topogeo_id = (network.topo_geom).id
where edge_id = relation.element_id;

select * from route_edges;

select routes.cheapest_path((select min(pk) from routes.nodes),(select max(pk) from routes.nodes))
