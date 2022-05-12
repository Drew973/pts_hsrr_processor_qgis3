CREATE OR REPLACE FUNCTION hsrr.score(run_geom geometry,sec_geom geometry)
RETURNS float AS $$
	select ST_HausdorffDistance(run_geom,sec_geom)
$$ LANGUAGE sql;