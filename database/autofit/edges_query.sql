


set search_path to hsrr,public;

--drop table if exists public.grouped_runs;

--create table public.grouped_runs as

drop table if exists test_edges;

create table public.test_edges as


select * from (
	select run,sec,has_forward,has_reverse
	,meas_len*st_lineLocatePoint(geom,st_startPoint(overlap)) as start_sec_ch
	,meas_len*st_lineLocatePoint(geom,st_endPoint(overlap)) as end_sec_ch
	,(max-min)*st_lineLocatePoint(run_geom,st_startPoint(overlap)) as start_run_ch
	,(max-min)*st_lineLocatePoint(run_geom,st_endPoint(overlap)) as end_run_ch
	,overlap

	from
		(
		select run,sec,min,max,run_geom,geom,meas_len,has_forward,has_reverse,st_intersection(run_geom,buffer) as overlap from 
		(
			select run,min(s_ch),max(e_ch),ST_MakeLine(array_agg(vect order by s_ch asc)) as run_geom 
			from readings 
			where st_length(vect)<1000 and run = 'A160 EB CL1'
			group by run
		) run

		inner join network on st_intersects(buffer,run_geom)
		) a

)b
where (has_forward and start_sec_ch<end_sec_ch) or (has_reverse and start_sec_ch>end_sec_ch)

;