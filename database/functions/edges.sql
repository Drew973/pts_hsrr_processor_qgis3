/*
find edges starting at row of route_nodes
*/

CREATE OR REPLACE FUNCTION edges(row_numb bigint,rn text,rch float,topology_node int,unfitted_cost float=10,length_tol float=100)
RETURNS table(start_row bigint,end_row bigint,cost float) AS $$

		with a as (select row_number,run_chainage,node_id from route_nodes where run=rn and run_chainage>rch)
		, b as (select row_number,run_chainage, run_geom(rn,numrange(rch::numeric,run_chainage::numeric)),geom from a inner join network_topo.edge on start_node=topology_node and end_node=node_id)
		
		select row_numb,row_number,(run_chainage-rch)*unfitted_cost from a
		union 
		select row_numb,row_number,mean_vertex_dist(geom,run_geom) from b where abs(st_length(run_geom)-(run_chainage-rch))<length_tol

$$ LANGUAGE sql immutable;