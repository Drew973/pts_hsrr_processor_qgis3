set search_path to hsrr,public;

CREATE OR REPLACE FUNCTION topology_based_autofit(rn text)
RETURNS table (pk int) AS $$

	select hsrr.calculate_possible_changes(rn);
	select hsrr.calculate_possible_edges(rn);
	
	delete from routes.edge;
	insert into routes.edge(start_node,end_node,cost,pk)
	select distinct on (start_node,end_node) start_node,end_node,cost,pk from hsrr.possible_edges order by start_node,end_node,cost;
	
	insert into hsrr.section_changes(run,sec,reversed,ch,pt,note)
	
	select rn,sec,rev,start_chainage,pt,'autofit_topology' from
	
	(
		select rn,sec,rev,start_chainage,st_startPoint(geom) as pt,
		 lag(sec) over(order by start_chainage,sec,rev) as last_sec
		 ,lag(rev) over(order by start_chainage,sec,rev) as last_rev

		from unnest(routes.cheapest_path(array( select pk from hsrr.possible_changes where node_id <0 order by ch,node_id)))
			inner join hsrr.possible_edges 
			on pk=unnest
	)a 
		where not (sec=last_sec and rev=last_rev) --avoid repeated rows
		
	returning pk;

$$ LANGUAGE sql;