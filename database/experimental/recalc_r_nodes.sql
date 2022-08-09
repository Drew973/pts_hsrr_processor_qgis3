
CREATE OR REPLACE FUNCTION hsrr.recalc_r_nodes(rn text)
RETURNS void AS $$

	truncate hsrr.r_nodes RESTART IDENTITY;

	with run_geoms as
	(
	select (st_dump(ST_LineMerge(ST_union(vect order by s_ch asc,50)))).geom as run_geom
	from hsrr.readings inner join hsrr.n_noded on st_dwithin(vect,the_geom,50) and run = rn
	)

	,run_ends as 
	(
	select st_startPoint(run_geom) as run_pt from run_geoms
	union
	select st_endPoint(run_geom) from run_geoms
	)

	insert into hsrr.r_nodes(run_pt,topo_pt,topo_pk)
	select run_pt,st_closestPoint(the_geom,run_pt),null from run_ends inner join hsrr.n_noded on st_dwithin(run_pt,the_geom,50)
	union
	select st_closestPoint(run_geom,the_geom),the_geom,id from hsrr.n_noded_vertices_pgr inner join run_geoms on st_dwithin(the_geom,run_geom,50);

	update hsrr.r_nodes set run_ch = hsrr.point_to_run_chainage(run_pt,rn);

$$ LANGUAGE sql;