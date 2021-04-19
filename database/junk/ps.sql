drop type if exists sec_dir cascade;


CREATE TYPE sec_dir AS
   (
     sec VARCHAR,
     rev bool
   );

--use like:
--select (sec,reversed)::sec_dir from routes

--g=geometry of vector
--measure of how likely vector v is in sect with geometry sect_geom. lower=less likely.
--based on distance and angle. discontinuity in nodes?
CREATE OR REPLACE FUNCTION likelyness(sect varchar,sect_geom geometry,v geometry,c_dist float=1,c_ang float=4,c_disc float=5) 
RETURNS float AS $$
	declare 
		--sect_geom geometry=geom from network where sec=sect;
		s float;
	 BEGIN	
	 	s=c_dist*st_distance(v,sect_geom)+c_ang*angle_to_sec(v,sect_geom);
		return -s;
	END;			
$$ LANGUAGE plpgsql;	
				
											
--returns cos(angle between v1 and nearest points on linestring geom)						
--v1=shorter geometry 
create or replace function angle_to_sec(v1 geometry,geom geometry)
returns float as $$
declare
		f1 float=ST_LineLocatePoint(geom,st_startpoint(v1));
		f2 float=ST_LineLocatePoint(geom,st_endpoint(v1));
begin
	if f1>=f2 then 
		return 1000;
	end if;
												   
	return cos_angle(v1,ST_makeLine(ST_LineInterpolatePoint(geom,f1),ST_LineInterpolatePoint(geom,f2)));

end;
$$ LANGUAGE plpgsql;
																						   
--returns sections in vect in buffer of and aligned with vect. Ordered by likelyness.
CREATE OR REPLACE FUNCTION ps(pt geometry,vect geometry,ca float=0.3,c_dist float=1,c_ang float=4,c_disc float=5)
RETURNS sec_dir[] AS $$											 
    BEGIN
		return array(
			select (sec,rev)::sec_dir from (select sec,likelyness(sec,geom,vect,c_dist,c_ang,c_dist),False as rev from network 
									   where st_contains(buff,pt) and vectors_align(vect,geom,ca) 
									  union 
									   select sec,likelyness(sec,geom,vect,c_dist,c_ang,c_dist),True as rev from network 
									   where not one_way and st_contains(buff,pt) and vectors_align(st_reverse(vect),geom,ca) 
									  ) a
			order by likelyness desc
			
					);
	END;			
$$ LANGUAGE plpgsql;


--returns sections vect in buffer of and aligned with vect. Ordered by likelyness.
CREATE OR REPLACE FUNCTION ps(pt geometry,vect geometry,ca float=0.3,c_dist float=1,c_ang float=4,c_disc float=5)
RETURNS sec_dir[] AS $$											 
    BEGIN
		return array(
			select (sec,rev)::sec_dir from (select sec,likelyness(sec,geom,vect,c_dist,c_ang,c_dist),False as rev from network 
									   where ST_Intersects(buff,vect) and vectors_align(vect,geom,ca) 
									  union 
									   select sec,likelyness(sec,geom,vect,c_dist,c_ang,c_dist),True as rev from network 
									   where not one_way and ST_Intersects(buff,vect) and vectors_align(st_reverse(vect),geom,ca) 
									  ) a
			order by likelyness desc
			
					);
	END;			
$$ LANGUAGE plpgsql;