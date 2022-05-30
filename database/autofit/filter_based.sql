

CREATE OR REPLACE FUNCTION hsrr.filtered_autofit(rn text)
RETURNS table (pk int) AS $$

	with a as (
	select *,lead(start_run_ch) over (order by start_run_ch) from hsrr.get_edges(rn)
	where ST_HausdorffDistance(overlap,hsrr.network_geom(sec,start_sec_ch,end_sec_ch))<15
	)

	insert into hsrr.section_changes (run,sec,ch,start_sec_ch,end_sec_ch)
	select run,sec,start_run_ch,start_sec_ch,end_sec_ch from a --where end_run_ch<lead
	union 
	select run,'D',end_run_ch,null,null from a where end_run_ch<lead
	returning pk;
	
$$ LANGUAGE sql;