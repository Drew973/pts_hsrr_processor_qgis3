/*
higher cost =  worse fit.
average closest distance from reading to section_geom for readings within range.
sec_geom is part of section within section chainages. null for dummy.
*/
CREATE OR REPLACE FUNCTION hsrr.cost(rn text,start_run_ch numeric,end_run_ch numeric,sec_geom geometry)
RETURNS float AS $$
	select case
		when sec_geom is null then 
			20+100*abs(end_run_ch-start_run_ch)
		else
	 		(select avg(st_distance(vect,sec_geom)) 
			from hsrr.readings
			where run=rn and hsrr.to_numrange(s_ch,e_ch,'()')&&hsrr.to_numrange(start_run_ch,end_run_ch,'()')
			)
	end;
$$ LANGUAGE sql STABLE;--readings could change. 
--"A STABLE function cannot modify the database and is guaranteed to return the same results given the same arguments for all rows within a single statement"


