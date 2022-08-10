
--True if vect in opposite direction to sec_geom.
--null for circular section. no good way to tell direction (small rbt problems)
CREATE OR REPLACE FUNCTION hsrr.is_reverse_direction(sec_geom geometry('linestring',27700),vect geometry('linestring',27700))
RETURNS bool AS $$
	select case when st_isClosed(sec_geom) then
		null
	else
		st_lineLocatePoint(sec_geom,st_startPoint(vect))>st_lineLocatePoint(sec_geom,st_endPoint(vect))
	end$$ LANGUAGE sql immutable;	




/*
	trim towards network geom.
	to find new ends of run geom go from end of run geom to closest point on network geom.
	then closest point on run_geom to this.
		
	then consider splitting run_geom for roundabouts.
*/

CREATE OR REPLACE FUNCTION hsrr.tidy_run_geom(run_geom geometry('linestring',27700),network_geom geometry('linestring',27700))
RETURNS geometry('linestring',27700)[] AS $$

		with a as 	
		(
		select ST_LineSubstring(run_geom
		,st_lineLocatePoint(run_geom,st_closestPoint(run_geom,st_closestPoint(network_geom,st_startpoint(run_geom))))
		,st_lineLocatePoint(run_geom,st_closestPoint(run_geom,st_closestPoint(network_geom,st_endpoint(run_geom))))
		) as g
		)
		
		select case when st_isClosed(network_geom) then
			array(select (st_dump(st_split(g,st_closestPoint(run_geom,st_startpoint(network_geom))))).geom from a)
		else
			array(select g from a)
		end
		
	end$$ LANGUAGE sql immutable;	
	
	
	
	


/*
	sections+chainages for run rn.
	does not include dummys.
	
	join readings to network on readings geometry within buffer.
	buffers in network should extend past ends of section for best results.
	st_buffer(geom,20)
	
	group by section+direction(handles change of direction)
	
	merge ajacent parts of run geometry within buffer (makes.multilinestring).
	split this into linestrings. (handles gaps,run left network,repeated section)
	
	move ends of run_geoms towards ends of sections by going to nearest point of section then to nearest point of run_geom.
	
	lookup run chainage from ends of these.
	round chainages to nearest 1m.
	
*/

CREATE OR REPLACE FUNCTION hsrr.fitting_options(rn text)
RETURNS table (sec text,start_sec_ch numeric,end_sec_ch numeric,start_run_ch numeric,end_run_ch numeric,run_geom geometry('linestring',27700)) AS $$

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

	, b as (select sec,network_geom,meas_len,unnest(hsrr.tidy_run_geom(run_geom,network_geom)) as run_geom from a)
	
	select sec
	,(meas_len*st_linelocatePoint(network_geom,st_startPoint(run_geom)))::numeric(9,3) as start_sec_ch
	,(meas_len*st_linelocatePoint(network_geom,st_endPoint(run_geom)))::numeric(9,3) as end_sec_ch
	,hsrr.point_to_run_chainage(st_startPoint(run_geom),rn)::numeric(9,3) as start_run_ch--closest point of run_geom to closest point of sec_geom to start.
	,hsrr.point_to_run_chainage(st_endPoint(run_geom),rn)::numeric(9,3) as end_run_ch--closest point of run_geom to closest point of sec_geom to start.
	,run_geom
	from b
	where
	hsrr.point_to_run_chainage(st_startPoint(run_geom),rn)::numeric(9,3)
	<hsrr.point_to_run_chainage(st_endPoint(run_geom),rn)::numeric(9,3)
	
$$ LANGUAGE sql stable;