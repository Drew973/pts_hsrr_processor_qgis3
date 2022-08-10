

CREATE OR REPLACE FUNCTION hsrr.recalc_r_edges(rn text)
RETURNS void AS $$

	truncate hsrr.r_edges RESTART IDENTITY;

	with noded as
	(
	select old_id,source,target,the_geom from hsrr.n_noded where (select has_forward from hsrr.network where old_id=id)
	union
	select old_id,target,source,st_reverse(the_geom) from hsrr.n_noded where (select has_reverse from hsrr.network where old_id=id)
	)

	insert into hsrr.r_edges(source,target,run_geom,topo_geom,sec_id)
	select s.pk as source
	,e.pk as target
	,hsrr.run_geom(rn,s.run_ch::numeric,e.run_ch::numeric)
	,hsrr.line_between_points(the_geom,s.topo_pt,e.topo_pt)
	,old_id

	from 
	hsrr.r_nodes as s
	inner join
	hsrr.r_nodes as e
	on s.run_ch<e.run_ch-- not adding dummys here.

	inner join noded on
	((s.topo_pk = noded.source ) or (s.topo_pk is null and st_dwithin(s.topo_pt,the_geom,10)))
	and
	((e.topo_pk = noded.target ) or (e.topo_pk is null and st_dwithin(e.topo_pt,the_geom,10)))

	and st_lineLocatePoint(the_geom,s.topo_pt)<st_lineLocatePoint(the_geom,e.topo_pt);

	/*
	adding dummys here
	*/
	insert into hsrr.r_edges(source,target)
	select
	s.pk
	,e.pk

	from 
	hsrr.r_nodes as s
	inner join
	hsrr.r_nodes as e
	on s.run_ch<=e.run_ch;

	update hsrr.r_edges set cost = hsrr.cost(rn,(select run_ch::numeric from hsrr.r_nodes where pk=source),(select run_ch::numeric from hsrr.r_nodes where pk=target),topo_geom);

$$ LANGUAGE sql;

