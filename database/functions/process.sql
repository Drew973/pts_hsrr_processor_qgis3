set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION hsrr.process(sect text,rev bool,lane text) 
RETURNS void AS $$
	select hsrr.refit(sect,rev,lane);
	select hsrr.resize(sect,rev,lane);
	select hsrr.recalc_coverage(sect,rev,lane);
	$$
LANGUAGE sql;





create function hsrr.process_run(rn text) returns void as $$

	with a as 
	(
		select distinct sec,start_sec_ch>end_sec_ch as reversed,xsp from hsrr.section_changes where run = rn
	)

	select hsrr.refit(sec,reversed,xsp) from a;

	with a as 
	(
		select distinct sec,start_sec_ch>end_sec_ch as reversed,xsp from hsrr.section_changes where run = rn
	)

	select hsrr.resize(sec,reversed,xsp) from a;
	select hsrr.recalc_coverage();
	
	$$
	language sql
	
	
	
CREATE OR REPLACE FUNCTION hsrr.process() 
RETURNS void AS $$
	select hsrr.refit();
	select hsrr.update_resized();
	select hsrr.recalc_coverage();
	$$
LANGUAGE sql;