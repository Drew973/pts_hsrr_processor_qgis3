set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION dot_prod(g1 geometry,g2 geometry)-- needs linestrings not multilinestrings
RETURNS float AS $$		
    BEGIN
		return(ST_X(ST_EndPoint(g1))-st_X(st_StartPoint(g1)))*(ST_X(ST_EndPoint(g2))-st_X(st_StartPoint(g2)))+(ST_Y(ST_EndPoint(g1))-st_Y(st_StartPoint(g1)))*(ST_Y(ST_EndPoint(g2))-st_Y(st_StartPoint(g2)));
    END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION hsrr.cos_angle(g1 geometry,g2 geometry)-- needs linestrings not multilinestrings
RETURNS float AS $$	
	declare
		L1 float=st_length(g1);
		L2 float=st_length(g2);
    BEGIN

	if L1=0 or L2=0 then
		return null;
	else
		return hsrr.dot_prod(g1,g2)/(st_length(g1)*st_length(g2));
	end if;
    END;			
$$ LANGUAGE plpgsql;


/*
	returns circular_substring when startFraction<=endFraction.
	else returns startFraction to 1 and 1 to endFraction
*/
create or replace function circular_substring(g geometry,startFraction float,endFraction float)
returns geometry as $$	

begin
	if startFraction<=endFraction then 
		return ST_LineSubstring(g,startFraction,endFraction);
	end if;
	
	return ST_MakeLine(ST_LineSubstring(g,startFraction,1),ST_LineSubstring(g,0,endFraction));
		
end;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION lineSubstring(g geometry,startFraction float,endFraction float) 
RETURNS geometry AS $$
		Declare 
			s float = hsrr.clamp(startFraction,0::float,1::float);
			e float = hsrr.clamp(endFraction,0::float,1::float);
        BEGIN
			if e<s then
				return st_reverse(st_lineSubstring(g,e,s));
			else
				return st_lineSubstring(g,s,e);
			end if;
		END;	
		
$$ LANGUAGE plpgsql;



/*
returns cosine of angle between v1 and substring of v2
1 for parallel or opposite direction
*/
create or replace function ca(v1 geometry,v2 geometry)
returns float as $$
declare
		f1 float=ST_LineLocatePoint(v2,st_startpoint(v1));
		f2 float=ST_LineLocatePoint(v2,st_endpoint(v1));
begin
	return case when st_isClosed(v1) then hsrr.cos_angle(v1,hsrr.circular_substring(v2,f1,f2))
	else hsrr.cos_angle(v1,st_makeLine(ST_LineInterpolatePoint(v2,f1),ST_LineInterpolatePoint(v2,f2))) end ;
end;
$$ LANGUAGE plpgsql;



--v1=shorter geometry 
create or replace function vectors_align(v1 geometry,v2 geometry,ca float=0.7)
returns bool as $$
declare
		f1 float=ST_LineLocatePoint(v2,st_startpoint(v1));
		f2 float=ST_LineLocatePoint(v2,st_endpoint(v1));
begin
	if f1>=f2 then 
		return False;
	end if;
	if cos_angle(v1,ST_makeLine(ST_LineInterpolatePoint(v2,f1),ST_LineInterpolatePoint(v2,f2)))>=ca then 
		return true;
	else
		return false;
	end if;
end;
$$ LANGUAGE plpgsql;

alter function vectors_align set search_path to hsrr,public;

