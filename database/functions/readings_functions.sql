

CREATE OR REPLACE FUNCTION hsrr.run_geom(rn text,start_run_ch numeric,end_run_ch numeric)
RETURNS geometry('multilinestring',27700) AS $$

		select ST_Multi(ST_MakeLine(
			array(
				select st_lineSubstring(vect,greatest((start_run_ch-s_ch)/(e_ch-s_ch),0),least((end_run_ch-s_ch)/(e_ch-s_ch),1))
				from hsrr.readings where run=rn and hsrr.to_numrange(s_ch,e_ch,'()')&&hsrr.to_numrange(start_run_ch,end_run_ch,'()') 
				  order by s_ch
			)
		))

$$ LANGUAGE sql stable;



CREATE OR REPLACE FUNCTION hsrr.point_to_run_chainage(pt geometry,rn text,dist float=50)-- needs linestrings not multilinestrings
RETURNS float AS $$	
		select s_ch+(e_ch-s_ch)*st_lineLocatePoint(vect,pt) from hsrr.readings where run=rn and st_dwithin(vect,pt,dist) order by st_distance(pt,vect) limit 1;
$$ LANGUAGE sql stable;



CREATE OR REPLACE FUNCTION hsrr.point_to_run_chainage(x float,y float,rn text,dist float=50)-- needs linestrings not multilinestrings
RETURNS float AS $$	
	select hsrr.point_to_run_chainage(ST_SetSRID(st_makePoint(x,y),27700),rn,dist)
$$ LANGUAGE sql stable;



--run chainage to point. Where chainage is duplicated returns earlier part of run.
CREATE OR REPLACE FUNCTION hsrr.run_ch_to_pt_s(ch numeric,rn text)
RETURNS geometry('Point',27700) AS $$
	select st_lineInterpolatePoint(vect,(ch-s_ch)/(e_ch-s_ch)) from hsrr.readings where run=rn and hsrr.to_numrange(s_ch,e_ch)@>ch order by e_ch desc limit 1;
$$ LANGUAGE sql stable;



--run chainage to point. Where chainage is duplicated returns later part of run.
--end of part of run. Gap after
CREATE OR REPLACE FUNCTION hsrr.run_ch_to_pt_e(ch numeric,rn text)
RETURNS geometry('Point',27700) AS $$
	select st_lineInterpolatePoint(vect,(ch-s_ch)/(e_ch-s_ch)) from hsrr.readings where run=rn and hsrr.to_numrange(s_ch,e_ch)@>ch order by s_ch asc limit 1;
$$ LANGUAGE sql stable;



--make linestring in espg27700 from coordinates in espg4326
--unused
CREATE OR REPLACE FUNCTION hsrr.make_run_geometry(start_lon float,start_lat float,end_lon float,end_lat float)
RETURNS geometry('linestring',27700) AS $$
select ST_MakeLine(St_Transform(ST_SetSRID(ST_makePoint(start_lon,start_lat),4326),27700),St_Transform(ST_SetSRID(ST_makePoint(end_lon,end_lat),4326),27700))
$$ LANGUAGE sql immutable;



