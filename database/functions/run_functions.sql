--interpolate point from readings at ch. ch is in km.
--returns null where run doesn't exist of no reading at this chainage.
CREATE OR REPLACE FUNCTION run_ch_to_pt(rn text,ch numeric)
RETURNS geometry('point') AS $$	
Declare
    BEGIN
		if ch%0.1=0 then
			return st_startpoint(vect) from readings where run=rn and s_ch=ch;
		end if;
		
		return ST_LineInterpolatePoint((select vect from readings where run=rn and s_ch<=ch and ch<e_ch),ch%0.1);
		END;			
$$ LANGUAGE plpgsql;


alter function run_ch_to_pt(rn text,ch numeric) set search_path to hsrr,public;

--select run_ch_to_pt('A69 DBFO EB CL1',0)




CREATE OR REPLACE FUNCTION pt_to_run_ch(rn text,pt geometry,tol float=50)
RETURNS numeric AS $$	
		select s_ch+0.1*st_lineLocatePoint(vect,pt)::numeric from readings where run=rn and st_dwithin(vect,pt,tol) order by st_distance(pt,vect) limit 1
$$ LANGUAGE sql IMMUTABLE;

alter function pt_to_run_ch set search_path to hsrr,public;