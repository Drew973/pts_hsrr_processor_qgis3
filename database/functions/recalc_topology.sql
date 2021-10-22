--recalculates topology data.
--needs doing after changing/initializing network.
CREATE OR REPLACE FUNCTION recalc_topology(tol float=5) 
RETURNS bool as	$$	

begin
	perform topology.dropTopology ('network_topo');
	perform topology.createTopology('network_topo', 27700, tol);
	perform topology.AddTopoGeometryColumn('network_topo','hsrr','network','topo_geom','lineString');
	alter table network_topo.edge_data add column sec text;
	update network set topo_geom=topology.toTopoGeom(geom, 'network_topo', 1);
	
--	perform pg_sleep(10);--need to wait for trigger events here.
	

	update network_topo.edge_data set sec = network.sec 
	from hsrr.network inner join network_topo.relation  
		on (topo_geom).id = topogeo_id 
	where edge_data.edge_id = relation.element_id;
	
	return True;
	end;
$$ LANGUAGE plpgsql;
