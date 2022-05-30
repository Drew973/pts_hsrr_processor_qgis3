CREATE OR REPLACE FUNCTION hsrr.cost(run text,start_run_ch numeric,end_run_ch numeric,sec text,start_sec_ch numeric,end_sec_ch numeric,run_geom geometry)
RETURNS float AS $$

	Declare 
		sec_geom geometry = hsrr.network_geom(sec,start_sec_ch,end_sec_ch);
	BEGIN

	if sec = 'D' then
		return 200+1000*(end_run_ch-start_run_ch);
	end if;

	return ST_FrechetDistance(run_geom,sec_geom);
	END;
$$ LANGUAGE plpgsql;