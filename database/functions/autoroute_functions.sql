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



--independent
CREATE OR REPLACE FUNCTION srs_between_points(a geometry,b geometry,tol float=50)
RETURNS sec_rev[] AS $$	
Declare	
    BEGIN
		return array(
			with c as(
			select (sec,false)::sec_rev as sr,geom from network where st_dwithin(a,geom,tol) and st_dwithin(b,geom,tol) and (rbt or st_lineLocatePoint(geom,a)<st_lineLocatePoint(geom,b))
			union
			select (sec,true)::sec_rev as sr,geom from network where (not one_way) and st_dwithin(a,geom,tol) and st_dwithin(b,geom,tol) and (rbt or st_lineLocatePoint(geom,a)>st_lineLocatePoint(geom,b))
			)
			select sr from c order by st_distance(geom,a)+st_distance(geom,b)
		);
	END;	
$$ LANGUAGE plpgsql;

alter function srs_between_points set search_path to hsrr,publicsele


CREATE OR REPLACE FUNCTION autofit(rn text)
RETURNS void AS $$	
insert into section_changes(run,sec,reversed,ch,pt,note)
select run,(srs[1]).sec,(srs[1]).rev,ch,pt,'auto' from autofit;
$$ LANGUAGE sql;

alter function autofit set search_path to hsrr,public;



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
		return ST_LineInterpolatePoint(vect,ch-s_ch) from readings where run=rn and s_ch<=ch and ch<= e_ch;
	END;
$$ LANGUAGE plpgsql;

alter function run_ch_to_pt set search_path to hsrr,public;
