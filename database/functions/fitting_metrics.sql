drop type if exists fitting_opt cascade;


create type fitting_opt as
(run varchar,sec varchar,rev bool,rg int8range);




--opts are made from array_clluster of all possible sec_revs from readings.
--should contain all correct opts+some wrong ones. metrics for finding these.



--distance from ends of section to nearest point in opts.
--good against slip roads. >50 is usually slip road
--high for 1st and last opt of run
CREATE OR REPLACE FUNCTION ends_dist(opt fitting_opt)
RETURNS float AS $$	
Declare
	g geometry = geom from network where sec=(opt).sec;
	dist_s float = (select min(ST_Distance(st_startPoint(g),vect)) from readings where run=(opt).run and (opt).rg @> f_line::bigint);
	dist_e float = (select min(ST_Distance(st_endPoint(g),vect)) from readings where run=(opt).run and (opt).rg @> f_line::bigint);
	
    BEGIN
		return dist_s+dist_e;
	
						  
	END;			
$$ LANGUAGE plpgsql;


--count of all opts in run overlapping by more than 1 f_line and pk!=k
CREATE OR REPLACE FUNCTION overlap_count(opt fitting_opt,k int)
RETURNS int AS $$	
Declare	
    BEGIN
		return count(pk) from routes where pk!=k and run=(opt).run and int8range(s_line,e_line)&&(opt).rg and upper(int8range(s_line,e_line)*(opt).rg)-lower(int8range(s_line,e_line)*(opt).rg)>1;
						  
	END;			
$$ LANGUAGE plpgsql;


--distance from ends of opt to section.

CREATE OR REPLACE FUNCTION ends_dist2(opt fitting_opt)
RETURNS float AS $$	
Declare
	g geometry = geom from network where sec=(opt).sec;
	start_geom geometry = st_startPoint(vect) from readings where run=(opt).run and f_line=lower((opt).rg);
	end_geom geometry = st_startPoint(vect) from readings where run=(opt).run and f_line=lower((opt).rg);
	
    BEGIN
		return st_distance(start_geom,geom)+st_distance(end_geom,geom);
	
						  
	END;			
$$ LANGUAGE plpgsql;



--distance from start of opt to section.
CREATE OR REPLACE FUNCTION start_dist(opt fitting_opt)
RETURNS float AS $$	
Declare
	g geometry = geom from network where sec=(opt).sec;
	start_geom geometry = vect from readings where run=(opt).run and f_line=lower((opt).rg);
    BEGIN
		return st_distance(start_geom,g);--+st_distance(end_geom,g);					  
	END;			
$$ LANGUAGE plpgsql;



--distance from end of opt to section.
CREATE OR REPLACE FUNCTION end_dist(opt fitting_opt)
RETURNS float AS $$	
Declare
	g geometry = geom from network where sec=(opt).sec;
	end_geom geometry = vect from readings where run=(opt).run and f_line=upper((opt).rg)-1;
    BEGIN
		return st_distance(end_geom,g);--+st_distance(end_geom,g);					  
	END;			
$$ LANGUAGE plpgsql;

--select *,ends_dist((run,sec,reversed,int4range(s_line,e_line,'[]'))::fitting_opt) from routes;