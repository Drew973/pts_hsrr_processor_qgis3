CREATE OR REPLACE FUNCTION hsrr.simple_autofit(rn text)
RETURNS table (pk int) AS $$

	with a as
	(
	select run,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch
	,lead(start_run_ch) over(order by start_run_ch)
	from hsrr.get_edges(rn)
	)
	
	insert into hsrr.section_changes(run,ch,sec,start_sec_ch,end_sec_ch)
	select run,start_run_ch,sec,start_sec_ch,end_sec_ch from a
	union
	select run,end_run_ch,'D',0,0 from a where lead-end_run_ch>0.001--dummys where >0.001 km gap
		
	returning pk;
	
$$ LANGUAGE sql;








CREATE OR REPLACE FUNCTION hsrr.simple_autofit(rn text)
RETURNS table (pk int) AS $$
	
	insert into hsrr.section_changes(run,ch,sec,start_sec_ch,end_sec_ch)
	select run,start_run_ch,sec,start_sec_ch,end_sec_ch
	from hsrr.get_edges(rn)
	union
	select rn,unnest(hsrr.readings_gaps(rn)),'D',0,0
		
	returning pk;
	
$$ LANGUAGE sql;




--adds every possible section.

CREATE OR REPLACE FUNCTION hsrr.simple_autofit(rn text)
RETURNS table (pk int) AS $$
	
	insert into hsrr.section_changes(run,ch,e_ch,sec,start_sec_ch,end_sec_ch)
	select run,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch
	from hsrr.get_edges(rn)		
	returning pk;
	
$$ LANGUAGE sql;


select * from hsrr.simple_autofit('SLIPS M1 SB RE')


--select hsrr.simple_autofit('SLIPS A1M SB CL1')

--todo: use readings_gaps to get gaps more reliabaly