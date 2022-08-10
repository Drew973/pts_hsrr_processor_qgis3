

/*
returns substring of geom, part is desired part of geom,fullrange is full length of geom.
*/

CREATE OR REPLACE FUNCTION hsrr.substring(geom geometry('linestring'),part numrange,fullRange numrange) 
	RETURNS geometry('linestring') AS $$
		declare 		
			s float =(lower(part*fullRange)-lower(fullRange))/(upper(fullRange)-lower(fullRange));
			e float =(upper(part*fullRange)-lower(fullRange))/(upper(fullRange)-lower(fullRange));
		begin
			if s<e and 0<=s and s<=1 and 0<=e and e<=1 then
				return st_lineSubstring(geom,s,e);
			else
				return null;
			end if;
		end;
	$$ language plpgsql;
	
/*	
select st_asText(hsrr.substring('LINESTRING(343855.059 556197.626,343885.905 556206.547,343949.137 556220.382,343998.494 556228.059,344033.328 556230.044,344046.303 556229.315)'::geometry
					  ,numrange(0,0.5)
					  ,numrange(0,2)))	
					  
					  
					  
*/





CREATE OR REPLACE FUNCTION hsrr.line_between_points(line_geom geometry('linestring'),start_point geometry('point'),end_point geometry('point'))
RETURNS geometry('linestring') AS $$	
		select case when st_lineLocatePoint(line_geom,start_point)>st_lineLocatePoint(line_geom,end_point) then
			st_reverse(st_lineSubstring(line_geom,st_lineLocatePoint(line_geom,end_point),st_lineLocatePoint(line_geom,start_point)))
		else
			st_lineSubstring(line_geom,st_lineLocatePoint(line_geom,start_point),st_lineLocatePoint(line_geom,end_point))
		end
		$$ LANGUAGE sql immutable;