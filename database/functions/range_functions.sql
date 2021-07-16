--split n into ranges with max length of len. last range may be shorter.
create or replace function to_ranges(n numeric,len numeric,bounds text='[)') 
	returns numrange[]
	as $$
	BEGIN
		return 
			array(select numrange(s::numeric,e::numeric,bounds)
				from
				(select s,coalesce(lead(s) over (order by s),n) as e from 
					(select generate_series(0.0,n,100) as s) a
				) b
				where s!=e
			);
		END;
	$$
	language plpgsql;


create or replace function length(rg numrange) 
	returns numeric
	as $$
	BEGIN
		return upper(rg)-lower(rg);
	END;
	$$
	language plpgsql;
