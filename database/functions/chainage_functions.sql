set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION hsrr.point_to_run_chainage(pt geometry,rn text,dist float=50)-- needs linestrings not multilinestrings
RETURNS float AS $$	
		select s_ch+(e_ch-s_ch)*st_lineLocatePoint(vect,pt) from hsrr.readings where run=rn and st_dwithin(vect,pt,dist) order by st_distance(pt,vect);
$$ LANGUAGE sql;


CREATE OR REPLACE FUNCTION hsrr.point_to_run_chainage(x float,y float,rn text,dist float=50)-- needs linestrings not multilinestrings
RETURNS float AS $$	
	select hsrr.point_to_run_chainage(ST_SetSRID(st_makePoint(x,y),27700),rn,dist)
$$ LANGUAGE sql;


CREATE OR REPLACE FUNCTION hsrr.run_chainage_to_x(ch float,rn text)
RETURNS float AS $$
	select st_x(st_lineInterpolatePoint(vect,(ch-s_ch)/(e_ch-s_ch))) from hsrr.readings where run=rn and s_ch<=ch and ch<=e_ch;
$$ LANGUAGE sql;


--select run_chainage_to_x(0,'A1M SB LE')


CREATE OR REPLACE FUNCTION hsrr.run_chainage_to_y(ch float,rn text)
RETURNS float AS $$
	select st_y(st_lineInterpolatePoint(vect,(ch-s_ch)/(e_ch-s_ch))) from hsrr.readings where run=rn and s_ch<=ch and ch<=e_ch;
$$ LANGUAGE sql;


--select run_chainage_to_y(0,'A1M SB LE')



CREATE OR REPLACE FUNCTION hsrr.point_to_sec_ch(x float,y float,sect text)
RETURNS float AS $$
	select meas_len*st_lineLocatePoint(geom,ST_SetSRID(st_makePoint(x,y),27700)) from hsrr.network where sec=sect;
$$ LANGUAGE sql;
--select hsrr.point_to_sec_ch(0,0,'4700A1/425')



CREATE OR REPLACE FUNCTION hsrr.sec_ch_to_point(ch float,sect text)
RETURNS geometry AS $$
	select case when meas_len>0 then st_lineInterpolatePoint(geom,hsrr.clamp(ch/meas_len,0,1))
	else null
	end
	
	from hsrr.network where sec=sect;
$$ LANGUAGE sql;


CREATE OR REPLACE FUNCTION hsrr.network_geom(sect text,start_sec_ch float,end_sec_ch float)
RETURNS geometry AS $$
	declare
		sec_len float = (select meas_len from hsrr.network where sec=sect);
		s float = hsrr.clamp(start_sec_ch/sec_len,0,1);
		e float = hsrr.clamp(end_sec_ch/sec_len,0,1);
	begin
		if s<e then
			return ST_LineSubstring(geom,s,e) from hsrr.network where sec=sect;
		else
			return st_reverse(ST_LineSubstring(geom,e,s)) from hsrr.network where sec=sect;
		end if;
	end;
$$ LANGUAGE plpgsql;