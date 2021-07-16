--pts21334_03_A69
set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION following_srs(pt geometry,tol float=20)
returns sec_rev[] as $$
    BEGIN
		return array(select (sec,False)::sec_rev from network where st_dwithin(pt,geom,tol) and st_linelocatePoint(geom,pt)*st_length(geom)<st_length(geom)-tol)--within distance and not end
		||array(select (sec,True)::sec_rev from network where st_dwithin(pt,geom,tol) and st_linelocatePoint(geom,pt)*st_length(geom)>tol and not one_way)--within distance and not start
		;
	END;	
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION previous_srs(pt geometry,tol float=20)
returns sec_rev[] as $$
    BEGIN
		return array(select (sec,False)::sec_rev from network where st_dwithin(pt,geom,tol) and st_linelocatePoint(geom,pt)*st_length(geom)>tol )--within distance and not start
		||array(select (sec,True)::sec_rev from network where st_dwithin(pt,geom,tol) and st_linelocatePoint(geom,pt)*st_length(geom)<st_length(geom)-tol and not one_way)--within distance and not end
		;
	END;	
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION srs_between_points(a geometry,b geometry,tol float=20)
RETURNS sec_rev[] AS $$	
Declare	srs sec_rev[]= array_intersect(following_srs(a,tol),previous_srs(b,tol));
    BEGIN
		return array(select unnest from unnest(srs) order by ends_dist(unnest,a,b));
	END;	
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION sr_between_points(a geometry,b geometry,tol float=20)
RETURNS sec_rev AS $$	
Declare	srs sec_rev[]= array_intersect(following_srs(a,tol),previous_srs(b,tol));
    BEGIN
		return unnest from unnest(srs) order by ends_dist(unnest,a,b) limit 1;
	END;	
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION ends_dist(sr sec_rev,a geometry,b geometry)
RETURNS float AS $$	
Declare	g geometry=geom from network where sec=(sr).sec;
    BEGIN
		return st_distance(a,g)+st_distance(b,g);
	END;	
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION run_ch_to_pt(rn text,ch numeric)
RETURNS geometry AS $$	
    BEGIN
		if ch%0.1=0 then
			return s_point from readings where run=rn and s_ch=ch;
		end if;
		
		return ST_LineInterpolatePoint((select vect from readings where run=rn and s_ch<=ch and ch<= e_ch),ch%0.1);
	END;	
$$ LANGUAGE plpgsql;

alter function run_ch_to_pt(rn text,ch numeric) set search_path to hsrr,public;

	
