
CREATE OR REPLACE FUNCTION possible_secs(pt geometry,vect geometry,ca float=0.3)
RETURNS varchar[] AS $$											 
    BEGIN
		return array(
			select sec||'#'||False from network where st_contains(buff,pt) and vectors_align(vect,geom,ca)
			union select sec||'#'||True from network where not one_way and st_contains(buff,pt) and vectors_align(vect,st_reverse(geom),ca)
					);
	END;			
$$ LANGUAGE plpgsql;


drop function if exists min_ps;

CREATE OR REPLACE FUNCTION min_ps(re varchar,sect varchar,x varchar,c int) 
	RETURNS int AS $$
	DECLARE
		min_ch int=c;
		s varchar;
		val varchar[]=possible_secs from ps where ref=re and ch=c limit 1;
	BEGIN
	if x='CL1' then 
		s=sect||'#'||False;
	else
		s=sect||'#'||True;
	end if;
	
	while s=any(val) loop
		min_ch=min_ch-10;
		val=possible_secs from ps where ref=re and ch=min_ch limit 1;
	end loop;

	return min_ch;
	END;			
$$ LANGUAGE plpgsql;


drop function if exists max_ps;
CREATE OR REPLACE FUNCTION max_ps(re varchar,sect varchar,x varchar,c int) 
	RETURNS int AS $$
	DECLARE
		max_ch int=c;
		s varchar;
		val varchar[]=possible_secs from ps where ref=re and ch=c limit 1;
	BEGIN
	if x='CL1' then 
		s=sect||'#'||False;
	else
		s=sect||'#'||True;
	end if;
	
	while s=any(val) loop
		max_ch=max_ch+10;
		val=possible_secs from ps where ref=re and ch=max_ch limit 1;
	end loop;

	return max_ch;
	END;			
$$ LANGUAGE plpgsql;

--select *,max_ps(ref,sec,xsp,s_ch) from auto_routes;

CREATE OR REPLACE FUNCTION better_s_ch(re varchar,sect varchar,rev bool,sch int) 
RETURNS int AS $$
	declare p geometry;
	s int;
	 BEGIN	
		 if rev then 
			p=(select st_endpoint(geom) from network where sec=sect limit 1);
		 else
			p=(select st_startpoint(geom) from network where sec=sect limit 1);
		 end if;
	 
	 	s=ch from ps where ref=re and sect||'#'||rev=any(possible_secs) and abs(ch-sch)<50 and st_dwithin(p,pt,30) order by st_distance(p,pt) limit 1;
		
	 	--s=ch from zm3 where ref=re and abs(ch-sch)<50 and st_dwithin(p,pt,30) order by st_distance(p,pt) limit 1;
		if s is null then
			return sch;
		else
			return s;
		end if;	
	END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION better_e_ch(re varchar,sect varchar,rev bool,sch int) 
RETURNS int AS $$
	declare p geometry;
	s int;
	 BEGIN	
		 if not rev then 
			p=(select st_endpoint(geom) from network where sec=sect limit 1);
		 else
			p=(select st_startpoint(geom) from network where sec=sect limit 1);
		 end if;
	 
	 	s=ch from ps where ref=re and sect||'#'||rev=any(possible_secs) and abs(ch-sch)<50 and st_dwithin(p,pt,30) order by st_distance(p,pt) limit 1;
		
	 	--s=ch from zm3 where ref=re and abs(ch-sch)<50 and st_dwithin(p,pt,30) order by st_distance(p,pt) limit 1;
		if s is null then
			return sch;
		else
			return s;
		end if;	
	END;			
$$ LANGUAGE plpgsql;