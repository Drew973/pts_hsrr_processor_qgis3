CREATE OR REPLACE FUNCTION to_nearest(n numeric,nearest int)
RETURNS int AS $$
	select nearest*(n/nearest)::int
$$ LANGUAGE sql;


CREATE OR REPLACE FUNCTION to_nearest(n numeric,nearest numeric)
RETURNS numeric AS $$
	select nearest*(n/nearest)::int
$$ LANGUAGE sql;


CREATE OR REPLACE FUNCTION to_nearest(n float,nearest numeric)
RETURNS float AS $$
	select nearest*(n/nearest)::int
$$ LANGUAGE sql;