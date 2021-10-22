set search_path to hsrr,network_topo,topology,public;

--select dropTopology ('network_topo');
--select createTopology('network_topo', 27700, 5);


--select topology.AddTopoGeometryColumn('network_topo','hsrr','network','topo_geom','lineString') as new_layer_id --1

--select * from network

--update network set topo_geom=topology.toTopoGeom(geom, 'network_topo', 1)

--select * from network


SELECT *
FROM edge,
     relation,
     network
WHERE edge.edge_id = relation.element_id
  AND relation.topogeo_id = (network.topo_geom).id



set search_path to hsrr,network_topo,topology,public;

select run
,mean_vertex_dist(edge.geom,run_geom.geom) as cost
,edge_id
,edge.geom
--,(select s from network where (topo_geom).id )
,(select topogeo_id from relation where edge.edge_id = relation.element_id)
,*
from run_geom inner join edge on st_dwithin(run_geom.geom,edge.geom,30)




drop view if exists test3;

create view test3 as select
row_number() over (order by run,row_number,edge_id) as id
,run
,row_number
,edge_id
,mean_vertex_dist(edge.geom,run_geom.geom) as cost
,case when (select one_way from network where (topo_geom).id = (select topogeo_id from relation where edge.edge_id = relation.element_id)) then -1
	else mean_vertex_dist(edge.geom,run_geom.geom) end as reverse_cost


,(select sec from network where (topo_geom).id = (select topogeo_id from relation where edge.edge_id = relation.element_id))
,edge.geom
--,(select s from network where (topo_geom).id )
from run_geom inner join edge on st_dwithin(run_geom.geom,edge.geom,30)




--options as
--id,run,s_ch,e_ch,cost,sec,reversed,source,target
--1 per edge. (want to split sections at nodes)



