set search_path to hsrr,public;


create or replace function get_pieces(sections varchar[]) 
	returns table (sect varchar,s_ch float,e_ch float)
	as $$
	BEGIN
		return QUERY
		select unnest as sec,(pieces).s_ch,(pieces).e_ch from (select unnest,get_pieces(unnest) as pieces from unnest(sections))a;
	END;
	$$
	language plpgsql;






DROP FUNCTION if exists get_pieces(character varying);

create or replace function get_pieces(sect varchar) 
	returns table (sec varchar,s_ch float,e_ch float,rg numrange,geom geometry) 
	
	as $$
	Declare ml numeric=meas_len(sect)::numeric;
	
	BEGIN
		return QUERY
			select sect
			,s::float
			,e::float
			,numrange(s::numeric,e::numeric)
			,get_line(sect,s,e)
			
			from
			(select s,coalesce(lead(s) over (order by s),ml) as e from 
			 	(select generate_series(0.0,ml,100) as s) a
			) b
			where s!=e;

		END;
	$$
	language plpgsql;
	

alter function get_pieces(sect varchar)  set search_path to hsrr,public;


--split n into ranges with max length of len. last range may be shorter.
create or replace function to_ranges(n numeric,len numeric,bounds text='[)') 
	returns numrange[]
	as $$
	select array(select numrange(s::numeric,e::numeric,bounds)
				from
				(select s,coalesce(lead(s) over (order by s),n) as e from 
					(select generate_series(0.0,n,len) as s) a
				) b
				where s!=e
				)
	$$
	language sql IMMUTABLE;
--select get_pieces('0600M6/152')