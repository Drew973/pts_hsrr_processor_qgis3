set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION generate_run_name(prefered text)
RETURNS text AS $$	
	DECLARE
		n int =0;
	
    BEGIN
	
		if not prefered in (select run from run_info) then
			return prefered;
		end if;

		while prefered||'_'||n in (select run from run_info) loop
			n = n+1;
		end loop;
		
		return prefered||'_'||n;
		
	END;			
$$ LANGUAGE plpgsql;

alter function generate_run_name set search_path to hsrr;

/*
tries to add to run_info.
returns new run or null
--path functions will be os specific.
--easier to just use os.path in python.
*/

CREATE OR REPLACE FUNCTION add_to_run_info(filename text,prefered text)
RETURNS text AS $$	
    Declare rn text = generate_run_name(prefered);
	BEGIN
		if (select count(run) from hsrr.run_info where file=filename)=0 then
			insert into run_info(run,file) values (rn,filename);
			return rn;
		end if;
		return null;
	END;			
$$ LANGUAGE plpgsql;


													   
alter function add_to_run_info set search_path to hsrr;




