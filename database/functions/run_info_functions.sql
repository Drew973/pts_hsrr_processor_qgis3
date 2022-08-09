
/*
generate unique name for run
*/
CREATE OR REPLACE FUNCTION hsrr.generate_run_name(prefered text)
RETURNS text AS $$	
	DECLARE
		n int =0;
	
    BEGIN
	
		if not prefered in (select run from hsrr.run_info) then
			return prefered;
		end if;

		while prefered||'_'||n in (select run from hsrr.run_info) loop
			n = n+1;
		end loop;
		
		return prefered||'_'||n;
		
	END;			
$$ LANGUAGE plpgsql;
--select (hsrr.generate_run_name('A1 SB RE'))



													   




