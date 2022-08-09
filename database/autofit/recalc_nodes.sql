	
	
CREATE OR REPLACE FUNCTION hsrr.recalc_route_nodes(rn text)
RETURNS void AS $$

truncate hsrr.route_nodes RESTART IDENTITY;
	
insert into hsrr.route_nodes(pt)

	with a as
	(select sec
	 ,(st_dump(ST_LineMerge(ST_union(st_intersection(vect,buffer) order by s_ch asc,50)))).geom as run_geom
	,hsrr.is_reverse_direction(geom,vect) as reversed
	,geom as network_geom
	,meas_len
	from hsrr.network inner join hsrr.readings on st_intersects(vect,buffer) and run = rn
	and ((hsrr.is_reverse_direction(geom,vect) and has_reverse) or (has_forward and not hsrr.is_reverse_direction(geom,vect) or hsrr.is_reverse_direction(geom,vect) is null))
	group by sec,hsrr.is_reverse_direction(geom,vect),network_geom,meas_len
	)
	
	, points as
	(
	select ST_ReducePrecision(st_closestPoint(run_geom,st_closestPoint(network_geom,st_startPoint(run_geom))),1) as pt from a
	union 
	select ST_ReducePrecision(st_closestPoint(run_geom,st_closestPoint(network_geom,st_endPoint(run_geom))),1)--snap to 1m grid.
	from a
	)
	select pt from points group by pt;
	
	
	update hsrr.route_nodes set run_ch = hsrr.point_to_run_chainage(pt,rn);
	
	insert into hsrr.route_nodes(run_ch,pt)
	select s_ch,ST_ReducePrecision(st_startPoint(vect),1) from hsrr.readings where run=rn order by s_ch limit 1
	on conflict do nothing;


	insert into hsrr.route_nodes(run_ch,pt)
	select e_ch,ST_ReducePrecision(st_endPoint(vect),1) from hsrr.readings where run=rn order by e_ch desc limit 1
	on conflict do nothing;

	$$ LANGUAGE sql;