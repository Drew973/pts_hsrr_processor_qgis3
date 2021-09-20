set search_path to categorizing,public;
--https://en.wikipedia.org/w/index.php?title=Spline_%28mathematics%29&oldid=288288033#Algorithm_for_computing_natural_cubic_splines


--using this means no dependency on postgis
drop type if exists spline_point cascade;
create type spline_point as
(
x numeric
,y numeric);


CREATE OR REPLACE FUNCTION y_diff(p1 spline_point,p2 spline_point)
RETURNS numeric AS $$
	select p1.y-p2.y
$$ LANGUAGE sql immutable;	

----select '{"(0,1)","(10,10)"}'::spline_point[]


drop type if exists cubic_spline_piece cascade;
create type cubic_spline_piece as
(
a numeric
, b numeric
, c numeric
, d numeric
,rg numrange--xrange for fit
);



drop type if exists cubic_spline cascade;
create type cubic_spline as
(
pieces cubic_spline_piece[]
);



--predict y from spline and x.
--correctly made spline will only have 1 range per x value.
CREATE OR REPLACE FUNCTION y(s cubic_spline_piece,x numeric)
RETURNS numeric AS $$
	declare v numeric = x-lower((s).rg);
	begin
		return (s).a+(s).b*v+(s).c*v*v+(s).d*v*v*v;
	END;			
$$ LANGUAGE plpgsql;	


--predict y from spline and x.
--correctly made spline will only have 1 range per x value.
CREATE OR REPLACE FUNCTION y(s cubic_spline,x numeric) 
RETURNS numeric AS $$
		select y(unnest,x) from unnest((s).pieces) where x<@(unnest).rg;
$$ LANGUAGE sql immutable;	



CREATE OR REPLACE FUNCTION fit_cubic_spline(points spline_point[])
RETURNS spline AS $$
	-- declare weight_sum numeric=sum((unnest).weight) from unnest(vals);
	 BEGIN	
		return null;
	END;			
$$ LANGUAGE plpgsql;	
