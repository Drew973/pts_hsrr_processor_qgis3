set search_path to hsrr,public;


create or replace function get_pieces(sect varchar) 
	returns table (s_ch float,e_ch float) 
	
	as $$
	Declare ml numeric=meas_len(sect)::numeric;
	
	BEGIN
		return QUERY
			select s::float as s_ch,e::float as e_ch from
			(select s,coalesce(lead(s) over (order by s),ml) as e from 
			 	(select generate_series(0.0,ml,100) as s) a
			) b
			where s!=e;

		END;
	$$
	language plpgsql;
	