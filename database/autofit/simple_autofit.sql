CREATE OR REPLACE FUNCTION hsrr.simple_autofit(rn text)
RETURNS table (pk int) AS $$

	insert into hsrr.routes(run,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch)
	select rn,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch from hsrr.fitting_options(rn)
	returning pk;
	
$$ LANGUAGE sql VOLATILE;