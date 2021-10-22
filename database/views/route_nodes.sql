set search_path to hsrr,public;


create materialized view route_nodes as

with a as(
select run,node_id,s_ch+st_lineLocatePoint(vect,n.geom) as run_chainage,n.geom 
from network_topo.node n inner join readings on st_dwithin(n.geom,vect,50)
union
select run,null,ch as run_ch,pt from gaps
)
select row_number() over(order by run,run_chainage),* from a;
