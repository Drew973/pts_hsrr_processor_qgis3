set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION clamp(val numeric,minimum numeric,maximum numeric) 
returns numeric as $$
			select least(greatest(val,minimum),maximum)
$$ LANGUAGE sql IMMUTABLE;


CREATE OR REPLACE FUNCTION clamp(val float,minimum float,maximum float) 
returns float as $$
			select least(greatest(val,minimum),maximum)
$$ LANGUAGE sql IMMUTABLE;