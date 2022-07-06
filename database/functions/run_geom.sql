CREATE OR REPLACE FUNCTION hsrr.run_geom(rn text,s numeric,e numeric)
RETURNS geometry('Multilinestring',27700) AS $$

	DECLARE 
		r numrange = hsrr.to_numrange(s,e);
	
	Begin

	return ST_Multi(st_linemerge(st_collect(
		
		st_lineSubstring
			(
			vect
			,(lower(hsrr.to_numrange(s_ch,e_ch)*r)-s_ch)/(e_ch-s_ch)--start fraction
			,(upper(hsrr.to_numrange(s_ch,e_ch)*r)-s_ch)/(e_ch-s_ch)--end fraction
			)
	
	))) from hsrr.readings where run=rn and hsrr.to_numrange(s_ch,e_ch)&&r;
	end;
	
$$ LANGUAGE plpgsql;



--select st_asText(hsrr.run_geom('A180 EB LE',0,10))