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