--shared
CREATE OR REPLACE FUNCTION ps(vect geometry('linestring',27700),ca float=0.3)
RETURNS sec_rev[] AS $$											 
    BEGIN
		return array(
			select sr from(
			select (sec,False)::sec_rev as sr,st_distance(vect,geom) as dist from network where st_intersects(buff,vect) and vectors_align(vect,geom,ca)
			union
			select (sec,True)::sec_rev as sr,st_distance(vect,geom) as dist from network where st_intersects(buff,vect) and vectors_align(st_reverse(vect),geom,ca) and not one_way
			)a order by dist
			);
	END;			
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION hsrr.autofit_run(rn varchar)
RETURNS void AS $$											 
    BEGIN
		update hsrr.readings set ps=ps(vect) where run=rn;
		update hsrr.readings set ps_text=cast(ps as varchar[]) where run=rn;
		delete from hsrr.routes where run=rn and note='auto';						  									   
		
		with a as (select ps[1] as p,unnest(array_cluster_int(array_agg(f_line),5)) from hsrr.readings where run=rn group by run,ps[1])
			,b as (select (p).sec as sec,(p).rev as rev,lower(unnest) as s,upper(unnest) as e from a)																											   																											   
			insert into hsrr.routes(run,sec,reversed,s_line,e_line,note) 										  
			select rn,sec,rev,s,e,'auto' from b
			where not sec is null;

	END;			
$$ LANGUAGE plpgsql




--autofit all possible sections
CREATE OR REPLACE FUNCTION hsrr.autofit_run(rn varchar)
RETURNS void AS $$
	DECLARE
		srs sec_rev[]=array(select DISTINCT unnest(ps) from hsrr.readings where run=rn);
	
    BEGIN
		update hsrr.readings set ps=ps(vect) where run=rn;
		update hsrr.readings set ps_text=cast(ps as varchar[]) where run=rn;
		delete from hsrr.routes where run=rn and note='auto';						  									   
		
		perform hsrr.insert_ps(rn,unnest(srs));--syntax

	END;			
$$ LANGUAGE plpgsql;
										 
						
										 
CREATE OR REPLACE FUNCTION hsrr.insert_ps(rn varchar,_ps sec_rev)
RETURNS void AS $$	
Declare
	a int4range[]=array_cluster_int(array(select f_line from hsrr.readings where run=rn and _ps=any(ps)),1);
										 
    BEGIN
										  
		if cardinality(a)>0 then
			insert into hsrr.routes(run,sec,reversed,s_line,e_line,note)
			select rn,_ps.sec,_ps.rev,lower(unnest) as s_line,upper(unnest)-1 as e_line,'auto' from unnest(a);
		end if;
										  
	END;			
$$ LANGUAGE plpgsql;	