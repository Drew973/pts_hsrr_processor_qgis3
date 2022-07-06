set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION hsrr.point_to_run_chainage(pt geometry,rn text,dist float=50)-- needs linestrings not multilinestrings
RETURNS float AS $$	
		select s_ch+(e_ch-s_ch)*st_lineLocatePoint(vect,pt) from hsrr.readings where run=rn and st_dwithin(vect,pt,dist) order by st_distance(pt,vect) limit 1;
$$ LANGUAGE sql immutable;


CREATE OR REPLACE FUNCTION hsrr.point_to_run_chainage(x float,y float,rn text,dist float=50)-- needs linestrings not multilinestrings
RETURNS float AS $$	
	select hsrr.point_to_run_chainage(ST_SetSRID(st_makePoint(x,y),27700),rn,dist)
$$ LANGUAGE sql immutable;



--run chainage to point. Where chainage is duplicated returns earlier part of run.
CREATE OR REPLACE FUNCTION hsrr.run_ch_to_pt_s(ch numeric,rn text)
RETURNS geometry('Point',27700) AS $$
	select st_lineInterpolatePoint(vect,(ch-s_ch)/(e_ch-s_ch)) from hsrr.readings where run=rn and hsrr.to_numrange(s_ch,e_ch)@>ch order by e_ch desc limit 1;
$$ LANGUAGE sql immutable;



--run chainage to point. Where chainage is duplicated returns later part of run.
--end of part of run. Gap after
CREATE OR REPLACE FUNCTION hsrr.run_ch_to_pt_e(ch numeric,rn text)
RETURNS geometry('Point',27700) AS $$
	select st_lineInterpolatePoint(vect,(ch-s_ch)/(e_ch-s_ch)) from hsrr.readings where run=rn and hsrr.to_numrange(s_ch,e_ch)@>ch order by s_ch asc limit 1;
$$ LANGUAGE sql immutable;



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


