CREATE OR REPLACE FUNCTION dot_prod(g1 geometry,g2 geometry)-- needs linestrings not multilinestrings
RETURNS float AS $$		
    BEGIN
		return(ST_X(ST_EndPoint(g1))-st_X(st_StartPoint(g1)))*(ST_X(ST_EndPoint(g2))-st_X(st_StartPoint(g2)))+(ST_Y(ST_EndPoint(g1))-st_Y(st_StartPoint(g1)))*(ST_Y(ST_EndPoint(g2))-st_Y(st_StartPoint(g2)));
    END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION cos_angle(g1 geometry,g2 geometry)-- needs linestrings not multilinestrings
RETURNS float AS $$	
	declare
		L1 float=st_length(g1);
		L2 float=st_length(g2);
    BEGIN

	if L1=0 or L2=0 then
		return null;
	else
		return dot_prod(g1,g2)/(st_length(g1)*st_length(g2));
	end if;
    END;			
$$ LANGUAGE plpgsql;


create or replace function ca(v1 geometry,v2 geometry)
returns float as $$
declare
		f1 float=ST_LineLocatePoint(v2,st_startpoint(v1));
		f2 float=ST_LineLocatePoint(v2,st_endpoint(v1));
begin
	return cos_angle(v1,ST_makeLine(ST_LineInterpolatePoint(v2,f1),ST_LineInterpolatePoint(v2,f2)));
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


