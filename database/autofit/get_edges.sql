*
function to find all possible sections for run.
chainages rounded to nearest multiple of round_to
*/
DROP FUNCTION hsrr.get_edges(text,numeric);

CREATE OR REPLACE FUNCTION hsrr.get_edges(rn text,round_to numeric=0.001)
RETURNS table (run text,start_run_ch numeric,end_run_ch numeric,sec text,start_sec_ch numeric,end_sec_ch numeric,run_geom geometry) AS $$

	with 
		merged as
			(
				select ST_LineMerge(ST_union(vect order by s_ch asc,50)) as run_geom
				from hsrr.readings
				where run = rn
				group by run
			)
	
	,intersections as
	(
		select sec,geom,meas_len,has_forward,has_reverse,st_intersection(run_geom,buffer) as overlap from 
			hsrr.network inner join merged
			on st_intersects(buffer,run_geom)
	)
		
	,c as
	(
	select sec,has_forward,has_reverse
	,meas_len*st_lineLocatePoint(geom,st_startPoint(overlap)) as start_sec_ch
	,meas_len*st_lineLocatePoint(geom,st_endPoint(overlap)) as end_sec_ch
	,to_nearest(hsrr.point_to_run_chainage(st_startPoint(overlap),rn),round_to) as start_run_ch
	,to_nearest(hsrr.point_to_run_chainage(st_endPoint(overlap),rn),round_to) as end_run_ch
	,overlap as run_geom
	from intersections
	)
	
	select rn,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,run_geom from c
	where (has_forward and start_sec_ch<end_sec_ch) or (has_reverse and start_sec_ch>end_sec_ch)
	
$$ LANGUAGE sql;


select * from hsrr.get_edges('SLIPS A1M SB CL1');