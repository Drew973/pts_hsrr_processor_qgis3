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

--path functions will be os specific.
--easier to just use os.path in python.


CREATE OR REPLACE FUNCTION add_to_run_info(filename text)
RETURNS text AS $$	
    Declare run text = generate_run_name(path_basename(filename));
	BEGIN
		insert into run_info(run,file) values (run,filename);
		return run;
	END;			
$$ LANGUAGE plpgsql;


													   
alter function add_to_run_info set search_path to hsrr;


*/
