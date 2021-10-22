CREATE OR REPLACE FUNCTION autofit(rn text)
RETURNS table (pk int) AS $$
	select calculate_possible_changes(rn);
	select calculate_possible_edges(rn);
	delete from routes.node;
	insert into routes.node(pk) select pk from possible_changes;
	delete from routes.edge;
	insert into routes.edge(start_node,end_node,cost,pk) select start_node,end_node,cost,pk from possible_edges;
	
	with a as (
	select *,(select ch from possible_changes where pk=start_node) as s_ch,(select ch from possible_changes where pk=end_node) as e_ch
	from unnest(routes.cheapest_path((select min(pk) from routes.node),(select max(pk) from routes.node)))

	inner join possible_edges on pk=unnest
	)
	insert into section_changes(run,sec,reversed,ch,pt)
	select rn,sec,rev,s_ch,st_startPoint(geom) from a order by s_ch
	returning pk
	
$$ LANGUAGE sql;