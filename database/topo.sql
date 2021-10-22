CREATE EXTENSION if not exists postgis_topology;
SET search_path = topology,public;
set search_path to hsrr,routes,public;


SELECT topology.DropTopology('network_topo');
SELECT topology.CreateTopology('network_topo', 27700);


SELECT topology.AddTopoGeometryColumn('network_topo', 'hsrr', 'network', 'topo_geom', 'LINESTRING');

UPDATE network SET topo_geom = topology.toTopoGeom(geom, 'network_topo', 1, 2);



set search_path to hsrr,public;

create view topo_edges as

with a as (
SELECT edge_id,start_node,end_node,sec,has_forward,has_reverse,e.geom
FROM network_topo.edge e,
     network_topo.relation rel,
     network r
WHERE e.edge_id = rel.element_id
  AND rel.topogeo_id = (r.topo_geom).id			
)

,b as
(
select start_node,end_node,sec,geom from a where has_forward
union
select end_node,start_node,sec,st_reverse(geom) from a where has_reverse
)

select row_number() over (order by start_node) as id,* from b;