CREATE OR REPLACE FUNCTION hsrr.process(rn varchar) 
	RETURNS void AS $$
	
	BEGIN
	perform hsrr.refit(rn);
	perform hsrr.resize(rn);
	END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION hsrr.process() 
	RETURNS void AS $$
	
	BEGIN
	perform hsrr.refit();
	perform hsrr.resize();
	END;			
$$ LANGUAGE plpgsql;



--sect=section label,r=reversed,x=xsp
CREATE OR REPLACE FUNCTION process(sect varchar,r bool,x varchar) 
	RETURNS void AS $$
	
		
	BEGIN
		perform refit(sect,r,x);
		perform resize(sect,r,x);
		perform recalc_coverage(sect,r,x);

	END;			
$$ LANGUAGE plpgsql;



alter function process(sect varchar,r bool,x varchar) set search_path to hsrr,public;