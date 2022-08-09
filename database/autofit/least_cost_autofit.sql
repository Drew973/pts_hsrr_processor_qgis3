--requires edges.sql and recalc_edges.sql 


create extension if not exists pgRouting;

CREATE OR REPLACE FUNCTION hsrr.least_cost_autofit(rn text)
RETURNS table (pk int) AS $$
	select hsrr.recalc_route_edges(rn);

	insert into hsrr.routes(run,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch)
	select rn,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch from pgr_dijkstra('select pk as id, source, target, cost from hsrr.route_edges'
					,(select pk from hsrr.route_nodes order by run_ch limit 1)::bigint--pk of first chainage in run
					,(select pk from hsrr.route_nodes order by run_ch desc limit 1)::bigint
					)--pk of last chainage in run
					
					inner join hsrr.route_edges on route_edges.pk = edge
					
	returning pk
	
$$ LANGUAGE sql;
