*
function to find all possible sections for run.
chainages rounded to nearest multiple of round_to
*/
DROP FUNCTION hsrr.get_edges(text,numeric);



CREATE OR REPLACE FUNCTION hsrr.get_edges(rn text,round_to numeric=0.001)
RETURNS table (run text,start_run_ch numeric,end_run_ch numeric,sec text,start_sec_ch numeric,end_sec_ch numeric,run_geom geometry) AS $$

	with 
	--merged run geom
		merged as
			(
				select ST_LineMerge(ST_union(vect order by s_ch asc,50)) as run_geom,min(s_ch),max(e_ch) 
				from hsrr.readings
				where run = rn
				group by run
			)
	
	,intersections as
	(
		select sec,geom,meas_len,has_forward,has_reverse,run_geom,min,max
			,st_intersection(run_geom,buffer) as overlap from 
			hsrr.network inner join merged
			on st_intersects(buffer,run_geom)
	)
		
	,c as
	(
	select sec,has_forward,has_reverse
	,meas_len*st_lineLocatePoint(geom,st_startPoint(overlap)) as start_sec_ch
	,meas_len*st_lineLocatePoint(geom,st_endPoint(overlap)) as end_sec_ch
		
	,hsrr.point_to_run_chainage(st_startPoint(overlap),rn) 
		as start_run_ch
		
	,hsrr.point_to_run_chainage(st_endPoint(overlap),rn) as end_run_ch
	,overlap as run_geom
	from intersections
	)
	
	select rn,to_nearest(start_run_ch,round_to),to_nearest(end_run_ch,round_to),sec,start_sec_ch,end_sec_ch,run_geom from c
	where (has_forward and start_sec_ch<end_sec_ch) or (has_reverse and start_sec_ch>end_sec_ch)
	
$$ LANGUAGE sql immutable;







CREATE OR REPLACE FUNCTION hsrr.get_edges(rn text,round_to numeric=0.001)
RETURNS table (run text,start_run_ch numeric,end_run_ch numeric,sec text,start_sec_ch numeric,end_sec_ch numeric,run_geom geometry) AS $$

with a as
(
select sec,has_forward,has_reverse,s_ch,e_ch
,st_lineLocatePoint(geom,st_startPoint(vect))*meas_len as start_sec_ch
,st_lineLocatePoint(geom,st_endPoint(vect))*meas_len as end_sec_ch
,st_lineLocatePoint(geom,st_startPoint(vect))*meas_len>st_lineLocatePoint(geom,st_endPoint(vect))*meas_len as reversed
,st_intersection(vect,buffer) as m
,hsrr.to_numrange(s_ch,e_ch,'[]') as r
from hsrr.readings inner join hsrr.network on st_intersects(buffer,vect)
and run = rn
)


--split by rg. change of direction
,b as
(
select sec,reversed,unnest(range_agg(r)) as rg
from a
where (not reversed and has_forward) or (reversed and has_reverse)
group by sec,reversed
)

, c as
(
--split by geometry. need to do to split where gaps in readings or when leaves buffer.
select sec,reversed
,(select geom from hsrr.network where network.sec=b.sec) as network_geom
--overlap of geom
,(st_dump((select st_linemerge(st_collect(m)) from a where rg@>r and a.sec=b.sec and a.reversed=b.reversed limit 1))).geom as run_geom
from b
)

,d as 
(
select sec,reversed,network_geom
	--nearest point on run_geom to nearest point of sec to start. significant for roundabouts.
	,st_closestPoint(run_geom,st_closestPoint(network_geom,st_startPoint(run_geom))) as sp
	,st_closestPoint(run_geom,st_closestPoint(network_geom,st_endPoint(run_geom))) as ep
	,run_geom
from c
)

select rn
--will be correct readings as startPoint along vect
,hsrr.to_nearest(hsrr.point_to_run_chainage(sp,rn),round_to)
,hsrr.to_nearest(hsrr.point_to_run_chainage(ep,rn),round_to)
,sec
,hsrr.to_nearest(st_lineLocatePoint(network_geom,sp)*hsrr.meas_len(sec),round_to) as start_sec_ch
,hsrr.to_nearest(st_lineLocatePoint(network_geom,ep)*hsrr.meas_len(sec),round_to) as end_sec_ch
,run_geom
from d
	
$$ LANGUAGE sql immutable;





select * from hsrr.get_edges('SLIPS A1M SB CL1');