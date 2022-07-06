CREATE OR REPLACE FUNCTION hsrr.get_pieces(sect text,piece_length numeric =0.1) 
RETURNS table(s numeric,e numeric,g geometry,r numrange) AS $$
		Declare
			m numeric;
			g geometry(linestring,27700);

        BEGIN
		select meas_len,geom from hsrr.network into m,g where sec=sect;
		
		return query 
			with a as (select generate_series(0,m,piece_length) as start_chain)
			, b as (select start_chain,least(start_chain+piece_length,m) as end_chain from a)
			
			select start_chain
			,end_chain
			,ST_LineSubstring(g,(start_chain/m)::float,(end_chain/m)::float)
			,numrange(least(start_chain,end_chain),greatest(start_chain,end_chain))
			from b where start_chain!=end_chain;
	
		END		
$$
LANGUAGE plpgsql;



--select s,e,st_asText(g) from hsrr.get_pieces('2000M18/145')