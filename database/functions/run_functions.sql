--interpolate point from readings at ch. ch is in km.
--returns null where run doesn't exist of no reading at this chainage.
CREATE OR REPLACE FUNCTION run_ch_to_pt(rn varchar,ch numeric)
RETURNS geometry('point') AS $$	
Declare
    BEGIN
		if ch%0.1=0 then
			return s_point from readings where run=rn and s_ch=ch;
		end if;
		
		return ST_LineInterpolatePoint((select vect from readings where run=rn and s_ch<=ch and ch<= e_ch),ch%0.1);
		END;			
$$ LANGUAGE plpgsql;



--select run_ch_to_pt('A69 DBFO EB CL1',0)