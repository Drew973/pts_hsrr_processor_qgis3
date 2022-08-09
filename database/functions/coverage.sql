set search_path to hsrr,public;

CREATE OR REPLACE FUNCTION hsrr.coverage(sect varchar,x text,r bool) 
RETURNS float AS $$
Declare
	should_be int=count(sec) from hsrr.resized where sec=sect and reversed=r and xsp=x;
	have int=count(sec) from hsrr.resized where sec=sect and reversed=r and xsp=x and not rl is null;
	BEGIN
			
		if should_be=0 then
			return null;
		end if;
		
		return  100*have/should_be;
		
	END;			
$$ LANGUAGE plpgsql;


--efficient function to recalculate all coverages
CREATE OR REPLACE FUNCTION hsrr.recalc_coverage() 
	RETURNS void AS $$
	BEGIN
		update hsrr.requested set coverage=0;

		with h as (select sec,reversed,xsp,count(sec) as have from hsrr.resized where not rl is null group by sec,reversed,xsp)
		update hsrr.requested as r set coverage=have from h where r.sec=h.sec and r.xsp=h.xsp and r.reversed=h.reversed;


		with sb as (select sec,reversed,xsp,count(sec) as should_be from hsrr.resized group by sec,reversed,xsp)
			update hsrr.requested as r set coverage=100*coverage/should_be from sb where r.sec=sb.sec and r.xsp=sb.xsp and r.reversed=sb.reversed;

	
	END;			
$$ LANGUAGE plpgsql;


/*
recalculate coverage for section,xsp,direction
*/
CREATE OR REPLACE FUNCTION hsrr.recalc_coverage(sect text,xs text,rev bool) 
	RETURNS void AS $$
		update hsrr.requested set coverage = hsrr.coverage(sect,xs,rev) where sec=sect and xsp=xs and reversed=rev;
$$ LANGUAGE sql;



select * from hsrr.resized