

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


/*
tries to add to run_info.
returns new run or null
--path functions will be os specific.
--easier to just use os.path in python.
*/

CREATE OR REPLACE FUNCTION hsrr.add_to_run_info(filename text,prefered text)
RETURNS text AS $$	
    Declare rn text = hsrr.generate_run_name(prefered);
	BEGIN
		if (select count(run) from hsrr.run_info where file=filename)=0 then
			insert into hsrr.run_info(run,file) values (rn,filename);
			return rn;
		end if;
		return null;
	END;			
$$ LANGUAGE plpgsql;


													   




