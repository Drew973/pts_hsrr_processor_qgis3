CREATE OR REPLACE FUNCTION hsrr.readings_gaps(rn text)
RETURNS float[] AS $$

	with a as 
	(
	select e_ch,st_endpoint(vect) as e,lead(vect) over (order by s_ch) from hsrr.readings where run = rn 
	)
	select array(select e_ch from a where not st_dwithin(e,st_startPoint(lead),10))
	
$$ LANGUAGE sql;


--select hsrr.readings_gaps('SLIPS A64 WB RE')

/*
use to add dummys for for autofitting

*/