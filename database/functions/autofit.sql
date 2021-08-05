set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION autofit(rn text)
RETURNS void AS $$	
insert into hsrr.section_changes(run,sec,reversed,ch,pt,note)
select run,(srs[1]).sec,(srs[1]).rev,ch,pt,'auto' from autofit where run=rn;
$$ LANGUAGE sql;

alter function autofit set search_path to hsrr,public;


/*
--shared
CREATE OR REPLACE FUNCTION ps(vect geometry('linestring',27700),ca float=0.3)
RETURNS sec_rev[] AS $$											 
    BEGIN
		return array(
			select sr from(
			select (sec,False)::sec_rev as sr,st_distance(vect,geom) as dist from hsrr.network where st_intersects(buff,vect) and vectors_align(vect,geom,ca)
			union
			select (sec,True)::sec_rev as sr,st_distance(vect,geom) as dist from hsrr.network where st_intersects(buff,vect) and vectors_align(st_reverse(vect),geom,ca) and not one_way
			)a order by dist
			);
	END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION hsrr.remove_slips(rn varchar)
RETURNS void AS $$											 
    BEGIN
		delete from hsrr.routes where run=rn and (select funct from hsrr.network where hsrr.network.sec=hsrr.routes.sec)='slip road';
	END;			
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION hsrr.autofit_run(rn varchar)
RETURNS void AS $$											 
    BEGIN
		update hsrr.readings set ps=ps(vect) where run=rn;
		update hsrr.readings set ps_text=cast(ps as varchar[]) where run=rn;
		delete from hsrr.routes where run=rn and note='auto';						  									   
		
		with a as (select ps[1] as p,unnest(array_cluster_int(array_agg(f_line),1)) from hsrr.readings where run=rn group by run,ps[1])
			,b as (select (p).sec as sec,(p).rev as rev,lower(unnest) as s,upper(unnest) as e from a)																											   																											   
			insert into hsrr.routes(run,sec,reversed,s_line,e_line,note) 										  
			select rn,sec,rev,s,e,'auto' from b
			where not sec is null;

	END;			
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION hsrr.autofit_run(rn varchar)
RETURNS void AS $$											 
    BEGIN
		update hsrr.readings set ps=ps(vect) where run=rn;
		update hsrr.readings set ps_text=cast(ps as varchar[]) where run=rn;
		delete from hsrr.routes where run=rn and note='auto';						  									   
		
		insert into hsrr.routes(run,note,sec,reversed,s_line,e_line)								  
		with a as (select f_line,unnest(ps) as ps from hsrr.readings where run=rn),
		b as (select unnest(array_cluster_int(array_agg(f_line),1)) as rg,ps from a group by ps)
		select rn,'auto',(ps).sec,(ps).rev,lower(rg),upper(rg)-1 from b;
											  
	END;			
$$ LANGUAGE plpgsql;




--autofit all possible sections then filter.
CREATE OR REPLACE FUNCTION hsrr.autofit_run(rn varchar)
RETURNS void AS $$
	DECLARE
		srs sec_rev[]=array(select DISTINCT unnest(ps_text::sec_rev[]) from hsrr.readings where run=rn);--filter these?
	
    BEGIN
		--update hsrr.readings set ps=ps(vect) where run=rn;
		update hsrr.readings set ps_text=ps(vect)::varchar where run=rn;
		
		--srs=array(select DISTINCT unnest(ps) from hsrr.readings where run=rn);
		delete from hsrr.routes where run=rn and note='auto';						  									   
		
		perform hsrr.insert_ps(rn,unnest(srs));--syntax
		--delete from hsrr.routes where run=rn and note='auto' and hsrr.piece_angle(run,sec,reversed,s_line,e_line) <0.9;
		delete from routes where run=rn and note='auto' and overlap_count((run,sec,reversed,int8range(s_line,e_line))::fitting_opt,pk)>0 and ends_dist((run,sec,reversed,int8range(s_line,e_line))::fitting_opt)>80;

	END;			
$$ LANGUAGE plpgsql;
										 
				
		
--insert into routes all f_lines from run where _ps in possible section										 
CREATE OR REPLACE FUNCTION hsrr.insert_ps(rn varchar,_ps sec_rev)
RETURNS void AS $$	
Declare
	a int4range[]=array_cluster_int(array(select f_line from hsrr.readings where run=rn and _ps=any(ps_text::sec_rev[])),1);--_ps in ps
	--a int4range[]=array_cluster_int(array(select f_line from hsrr.readings where run=rn and _ps=(ps_text::sec_rev[])[1]),1);--_ps is 1st(most likely) ps.

    BEGIN
										  
		if cardinality(a)>0 then
			insert into hsrr.routes(run,sec,reversed,s_line,e_line,note)
			select rn,_ps.sec,_ps.rev,lower(unnest) as s_line,upper(unnest)-1 as e_line,'auto' from unnest(a);
		end if;
										  
	END;			
$$ LANGUAGE plpgsql;




CREATE OR REPLACE FUNCTION hsrr.piece_angle(rn varchar,sect varchar,rev bool,s_line int,e_line int)
RETURNS float AS $$	
	declare
		geom geometry('linestring')=(select geom from hsrr.network where hsrr.network.sec=sect);
		g geometry;
		s geometry('Point');
		e geometry('Point');
										  
    BEGIN
																									   
																										   
		if rev then
			s=(select s_point from hsrr.readings as r where r.run=rn and r.f_line=s_line);
			e=(select e_point from hsrr.readings as r where r.run=rn and r.f_line=e_line);
		else
			s=(select e_point from hsrr.readings as r where r.run=rn and r.f_line=e_line);
			e=(select s_point from hsrr.readings as r where r.run=rn and r.f_line=s_line);
		end if;
			   
		g=st_makeLine(st_closestPoint(geom,s),st_closestPoint(geom,e));
		return cos_angle(g,st_makeLine(s,e));																																			
										  
    END;			
$$ LANGUAGE plpgsql;


*/

