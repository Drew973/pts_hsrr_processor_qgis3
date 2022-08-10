
/*
	find nodes where section could change.
	find sections joining these.
	add dummys joining nodes to later nodes.
*/


CREATE OR REPLACE FUNCTION hsrr.recalc_route_edges(rn text)
RETURNS void AS $$
	--empty tables and reset sequences
	truncate hsrr.route_edges RESTART IDENTITY;
	
	select hsrr.recalc_route_nodes(rn);

	--add sections linking nodes to following nodes. 
	insert into hsrr.route_edges(source,start_run_ch,target,end_run_ch,sec,start_sec_ch,end_sec_ch)
	select 
		a.pk as source
		,a.run_ch as start_run_ch
		,b.pk as target
		,b.run_ch as end_run_ch
		,sec
		,st_linelocatePoint(geom,a.pt)*meas_len as start_sec_ch
		,st_linelocatePoint(geom,b.pt)*meas_len as end_sec_ch

	from hsrr.route_nodes as a inner join hsrr.route_nodes as b
	on b.run_ch>a.run_ch--ignore points less than 0.005km apart.

	inner join hsrr.network on st_dwithin(a.pt,geom,40) and st_dwithin(b.pt,geom,40)
	--and st_linelocatePoint(geom,a.pt)>0 and st_linelocatePoint(geom,b.pt)<1

	and (
		(has_forward and st_linelocatePoint(geom,a.pt)::numeric(9,3)<st_linelocatePoint(geom,b.pt)::numeric(9,3))
		or (has_reverse and st_linelocatePoint(geom,a.pt)::numeric(9,3)>st_linelocatePoint(geom,b.pt)::numeric(9,3))
		)
	
	and abs((b.run_ch-a.run_ch)-meas_len)<100--within 100m of meas_len.
	;
	
	/*dummys between chainage and every following (or identical)chainage.
	need dummy across gap in readings otherwise no way across without choosing incorrect dummy
	*/
	
	insert into hsrr.route_edges(start_run_ch,end_run_ch,source,target)
	select s.run_ch,e.run_ch,s.pk,e.pk--hsrr.cost(rn text,start_run_ch numeric,end_run_ch numeric,sec_geom geometry)
	from hsrr.route_nodes as s inner join hsrr.route_nodes as e on s.run_ch<=e.run_ch
	and s.pk!=e.pk;
	
	update hsrr.route_edges set cost = hsrr.cost(rn,start_run_ch,end_run_ch,hsrr.network_geom(sec,start_sec_ch,end_sec_ch));


$$ LANGUAGE sql;