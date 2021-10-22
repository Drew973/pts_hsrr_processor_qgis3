CREATE OR REPLACE FUNCTION run_geom(run text,chainage numrange)
RETURNS geometry AS $$
	 	--select ST_MakeLine( array(select vect from readings where run=run and rg&&chainage order by s_ch))
		select ST_MakeLine( array(select vect from readings where run=run and numrange(s_ch,e_ch)&&chainage order by s_ch))

$$ LANGUAGE sql immutable;