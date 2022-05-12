set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION hsrr.point_to_run_chainage(x float,y float,rn text,dist float=50)-- needs linestrings not multilinestrings
RETURNS float AS $$	
	declare
		pt geometry = ST_SetSRID(st_makePoint(x,y),27700);
    BEGIN
		return min(st_distance(pt,vect)) from hsrr.readings where run=rn and st_dwithin(vect,pt,dist);
	
    END;			
$$ LANGUAGE plpgsql;
--select point_to_run_chainage(505150,411086,'A180 EB CL1')



CREATE OR REPLACE FUNCTION hsrr.point_to_sec_ch(x float,y float,sect text)
RETURNS float AS $$
	select meas_len*st_lineLocatePoint(geom,ST_SetSRID(st_makePoint(x,y),27700)) from hsrr.network where sec=sect;
$$ LANGUAGE sql;
--select hsrr.point_to_sec_ch(0,0,'4700A1/425')



CREATE OR REPLACE FUNCTION hsrr.sec_ch_to_x(ch float,sect text)
RETURNS float AS $$
	select st_x(st_lineInterpolatePoint(geom,ch/meas_len)) from hsrr.network where sec=sect;
$$ LANGUAGE sql;
--select hsrr.sec_ch_to_x(0,'4700A1/425')


CREATE OR REPLACE FUNCTION hsrr.sec_ch_to_x(ch float,sect text)
RETURNS float AS $$
	select st_y(st_lineInterpolatePoint(geom,ch/meas_len)) from hsrr.network where sec=sect;
$$ LANGUAGE sql;
--select hsrr.sec_ch_to_x(0,'4700A1/425')