--requires edges.sql and recalc_edges.sql 


create extension if not exists pgRouting;


CREATE OR REPLACE FUNCTION hsrr.least_cost_autofit(rn text)
RETURNS table (pk int) AS $$
	select hsrr.recalc_edges(rn);

	insert into hsrr.section_changes(run,ch,e_ch,sec,start_sec_ch,end_sec_ch)
	select rn,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch from pgr_dijkstra('select pk as id, source, target, cost from hsrr.edges'
					,(select source from hsrr.edges order by start_run_ch limit 1)
					,(select target from hsrr.edges order by end_run_ch desc limit 1))
					
					inner join hsrr.edges on edges.pk = edge
					and sec!='D'
	returning pk
	
$$ LANGUAGE sql;


--select * from hsrr.least_cost_autofit('M621 SLIPS EB CL1');

/*
topology based:


calculate route_nodes.
	1 route node anywhere section could change.
		network nodes within distance of run.
		turning point in run (rare, errors here not big deal.)
		run left network.

	pk,run_ch,pt geometry(for debugging/display).
	
	
	

calculate possible sections/edges
	calculate from route_nodes.
	link to all following nodes by dummy. dummy cost =a*length + b . b is penalty for complexity (don't want several dummys in row).
	
	link to following nodes where section within distance and correct direction. and section chainage reasonable match to run chainages


/*