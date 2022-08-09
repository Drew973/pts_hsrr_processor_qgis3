CREATE OR REPLACE FUNCTION hsrr.meas_len(sect varchar) RETURNS float AS 
$$
SELECT cast(meas_len as float) from hsrr.network where sec=sect
$$ 
LANGUAGE sql stable;



CREATE OR REPLACE FUNCTION hsrr.network_geom(sect varchar,start_ch numeric,end_ch numeric) RETURNS geometry AS
$$
SELECT case 
	when end_ch>start_ch then 
		ST_LineSubstring(geom,greatest(start_ch/meas_len,0),least(end_ch/meas_len,1) )
	else
		st_reverse(ST_LineSubstring(geom,greatest(end_ch/meas_len,0),least(start_ch/meas_len,1) ))
	end
	from hsrr.network where sec=sect and meas_len>0

$$
LANGUAGE sql stable;


CREATE OR REPLACE FUNCTION hsrr.point_to_sec_ch(x float,y float,sect text)
RETURNS float AS $$
	select meas_len*st_lineLocatePoint(geom,ST_SetSRID(st_makePoint(x,y),27700)) from hsrr.network where sec=sect;
$$ LANGUAGE sql stable;
--select hsrr.point_to_sec_ch(0,0,'4700A1/425')



CREATE OR REPLACE FUNCTION hsrr.sec_ch_to_point(ch float,sect text)
RETURNS geometry AS $$
	select case when meas_len>0 then st_lineInterpolatePoint(geom,hsrr.clamp(ch/meas_len,0,1))
	else null
	end
	
	from hsrr.network where sec=sect;
$$ LANGUAGE sql stable;
