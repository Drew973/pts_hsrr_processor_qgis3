set search_path to hsrr,public;


/*
--splits len into pieces with length of step. last piece can have shorter length. 
create or replace function split_len(len numeric,step numeric) 
	returns table (s numeric,e numeric) 
	
	as $$
	BEGIN
			RETURN QUERY
			select st,en from
			(select generate_series as st,COALESCE(lead(generate_series)over (order by generate_series),len) as en from generate_series(0,len,step))a
			where st!=en
			;

		END;
	$$
	language plpgsql;
*/

--splits len into pieces with length of step. last piece can have shorter length. 
create or replace function split_len(len numeric,step numeric) 
returns numrange[] as $$
	select array(select numrange(st,en) from
	(select generate_series as st,COALESCE(lead(generate_series)over (order by generate_series),len) as en from generate_series(0,len,step))a
	where st!=en)
$$ language sql immutable;




DROP FUNCTION if exists split_len(geometry,numeric,numeric);
																																		
create or replace function split_len(geom geometry('linestring'),step numeric,len numeric=null) 
returns table (s numeric,e numeric,geo geometry('linestring')) 
	
as $$	
	BEGIN											 
		RETURN QUERY
		select st,en,make_line(L:=geom,start_ch:=st,end_ch:=en,len:=len) from
		(select generate_series as st,COALESCE(lead(generate_series)over (order by generate_series),len) as en from generate_series(0,len,step))a
		where st!=en
		;
	END;
$$
language plpgsql;																										
																																		
																																		
																																		

select * from split_len((select geom from network where sec='B3430/040'),10,585.76)