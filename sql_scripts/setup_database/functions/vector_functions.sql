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


--part of linestring  from start_ch to end_ch. len=noninal length. chainages in terms of nominal length

CREATE OR REPLACE FUNCTION make_line(L geometry('linestring'),len float,start_ch float,end_ch float) 
RETURNS geometry('linestring') AS $$
		declare
			f1 float;
			f2 float;
        BEGIN	
				f1=start_ch/len;
				f2=end_ch/len;
				
				if f1<0 then
					f1=0;
				end if;
				
				if f1>1 then
					f1=1;
				end if; 

				if f2>1 then
					f2=1;
				end if; 

				if f2<0 then
					f2=0;
				end if; 
				
				if f2>f1 then
					return ST_LineSubstring(L,f1,f2);
				else
					return st_reverse(ST_LineSubstring(L,f2,f1));
				end if;
													   
		END;			
$$ LANGUAGE plpgsql;