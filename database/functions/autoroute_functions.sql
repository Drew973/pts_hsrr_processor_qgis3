--pts21334_03_A69
set search_path to hsrr,public;



/*returns mean distance from vertices of g1 to nearest part of g2
*/
CREATE OR REPLACE FUNCTION mean_vertex_dist(g1 geometry,g2 geometry)
RETURNS float AS $$	

	with a as (select st_distance((st_dumpPoints(g1)).geom,g2) as dist)
	select sum(dist)/ST_NumPoints(g1) from a;
	
$$ LANGUAGE sql immutable;



/*
want measure(mean?,maximum?) of distance from readings vertices to nearest point on section.not sure if ST_HausdorffDistance does this.
make function to do this.

100m spacing means only vertices reliable on highly curved sections

--a is linestring 2+ points. more probably better
--tol is maximum distance between network and geoemtry
--min_cos is minimum cosine of angle between geometries. 0=90 degrees,1=0 degrees...
*/

CREATE OR REPLACE FUNCTION best_sr(a geometry,tol float=50,min_cos float =0)
RETURNS sec_rev AS $$	
--Declare	srs sec_rev[]= array_intersect(following_srs(a,tol),previous_srs(b,tol));
		with b as(
		select sec,False as reversed,geom from network where st_dwithin(geom,a,tol) and cos_angle(a,geom)>min_cos
		)
		select (sec,reversed)::sec_rev from b 
		order by mean_vertex_dist(a,geom)
		limit 1;
		
$$ LANGUAGE sql immutable;





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

alter function srs_between_points set search_path to hsrr,public;



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
