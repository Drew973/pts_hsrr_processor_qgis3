CREATE OR REPLACE FUNCTION hsrr.sequencial_score_autofit(rn text)
RETURNS table (pk int) AS $$

	with a as (select *,numrange(start_run_ch,end_run_ch) as r from hsrr.get_edges(rn))


	,e as (select *,numrange(ch,least(lead(ch) over (order by ch),ch+abs(start_sec_ch-end_sec_ch))) as r 
		   from hsrr.section_changes where run = rn order by ch)

	insert into hsrr.section_changes(run,ch,sec,start_sec_ch,end_sec_ch)
	select run,start_run_ch,sec,start_sec_ch,end_sec_ch from a 
		where (select count(sec) from a as b where b.score<a.score and a.r&&b.r) = 0
		and (select count(sec) from e where a.r&&e.r) = 0
	returning pk;
	
$$ LANGUAGE sql;
