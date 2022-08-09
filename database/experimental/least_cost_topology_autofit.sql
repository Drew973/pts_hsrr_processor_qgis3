CREATE OR REPLACE FUNCTION hsrr.least_cost_topology_autofit(rn text)
RETURNS table (pk int) AS $$
	select hsrr.recalc_r_nodes(rn);
	select hsrr.recalc_r_edges(rn);
	
	insert into hsrr.routes(sec,start_sec_ch,end_sec_ch,start_run_ch,end_run_ch)

	select sec
	,meas_len*st_lineLocatePoint(geom,st_startPoint(topo_geom)) as start_sec_ch
	,meas_len*st_lineLocatePoint(geom,st_endPoint(topo_geom)) as end_sec_ch
	,(select run_ch from hsrr.r_nodes where pk=source ) as start_run_ch
	,(select run_ch from hsrr.r_nodes where pk=target ) as end_run_ch


	from pgr_dijkstra('select pk as id, source, target, cost from hsrr.r_edges'
						,(select pk from hsrr.r_nodes order by run_ch limit 1)::bigint--pk of first chainage in run
						,(select pk from hsrr.r_nodes order by run_ch desc limit 1)::bigint
						)
						inner join hsrr.r_edges on pk=edge
						inner join  hsrr.network on network.id = sec_id

	returning pk;

$$ LANGUAGE sql;