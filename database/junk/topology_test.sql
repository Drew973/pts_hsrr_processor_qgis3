set search_path to hsrr,public,topology;

create extension if not exists postgis_topology;


--drop schema if exists network_topo cascade;
--delete from topology.topology where name='network_topo';
select DropTopology ('network_topo');

select createTopology('network_topo', 27700, 5);

alter table network_topo.edge_data add column sec text;--references hsrr.network on update cascade on delete cascade

drop table if exists topo_to_network;

create table topo_to_network as
with a as (select sec as sect,array(select TopoGeo_AddLineString('network_topo',geom)) as pks from network)
	select sect,pks from a;

--add sec

set search_path to hsrr,network_topo,public;

update network_topo.edge_data set sec = sect from topo_to_network where edge_id=any(pks);

update edge_data set sec=
		(select sec from network where st_dwithin(st_startPoint(edge_data.geom),network.geom,5) 
		  and st_dwithin(st_endPoint(edge_data.geom),network.geom,5) 
		  order by mean_vertex_dist(edge_data.geom,network.geom)
		 limit 1) 
		 where sec is null;




--calculating costs and filtering where not near readings
drop table if exists run_edges;

create table run_edges as

--todo make reverse cost negative for one way-will treat edge as irreversible
--use distance to network geom
with a as (select st_union(vect) as readings_geom from readings where run='SEW NB CL1')
select edge_id as id
,start_node as source
,end_node as target
,mean_vertex_dist(geom,readings_geom) as cost
,mean_vertex_dist(geom,readings_geom) as reverse_cost
,sec,
geom
from edge_data inner join a on st_dwithin(readings_geom,geom,50);


drop table if exists test2;

create table test2 as
select sec,id,geom FROM pgr_dijkstra('select id,source,target,cost,reverse_cost from run_edges' ,17,27)
inner join run_edges on edge=id
