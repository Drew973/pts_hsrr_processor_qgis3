/*
return substring of line_geom between points.
reverse direction where end_point closer to start of geometry than start_point
*/

CREATE OR REPLACE FUNCTION hsrr.line_between_points(line_geom geometry('linestring'),start_point geometry('point'),end_point geometry('point'))
RETURNS geometry('linestring') AS $$	
		select case when st_lineLocatePoint(line_geom,start_point)>st_lineLocatePoint(line_geom,end_point) then
			st_reverse(st_lineSubstring(line_geom,st_lineLocatePoint(line_geom,end_point),st_lineLocatePoint(line_geom,start_point)))
		else
			st_lineSubstring(line_geom,st_lineLocatePoint(line_geom,start_point),st_lineLocatePoint(line_geom,end_point))
		end
		$$ LANGUAGE sql immutable;