set search_path to hsrr,public;



CREATE OR REPLACE FUNCTION hsrr.get_edges(rn text,round_to numeric=0.001)
RETURNS table (run text,start_run_ch numeric,end_run_ch numeric,sec text,start_sec_ch numeric,end_sec_ch numeric,score float,overlap geometry) AS $$


select run,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,score,overlap from (
	select run,sec,has_forward,has_reverse
	,meas_len*st_lineLocatePoint(geom,st_startPoint(overlap)) as start_sec_ch
	,meas_len*st_lineLocatePoint(geom,st_endPoint(overlap)) as end_sec_ch
	,to_nearest((max-min)*st_lineLocatePoint(run_geom,st_startPoint(overlap)),round_to) as start_run_ch
	,to_nearest((max-min)*st_lineLocatePoint(run_geom,st_endPoint(overlap)),round_to) as end_run_ch
	,overlap
	,score(geom,overlap)

	from
		(
		select run,sec,min,max,run_geom,geom,meas_len,has_forward,has_reverse,st_intersection(run_geom,buffer) as overlap from 
		(
			select run,min(s_ch),max(e_ch),ST_MakeLine(array_agg(vect order by s_ch asc)) as run_geom 
			from hsrr.readings 
			where st_length(vect)<1000 and run = rn
			group by run
		) run

		inner join hsrr.network on st_intersects(buffer,run_geom)
		) a

)b
where (has_forward and start_sec_ch<end_sec_ch) or (has_reverse and start_sec_ch>end_sec_ch)
	
$$ LANGUAGE sql;


--select * from get_edges('A160 EB CL1')