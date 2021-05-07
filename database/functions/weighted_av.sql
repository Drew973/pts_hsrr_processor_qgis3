
--sum(length*val)/sum(length)
--weights[i] is weight for vals[i]

drop function if exists weighted_av;

CREATE OR REPLACE FUNCTION weighted_av(vals anyarray,weights anyarray) 
RETURNS anyelement AS $$
	 BEGIN	
		if array_sum(weights)=0 then
			return null;
		else			   
			return array_sum(array_multiply(vals,weights))/array_sum(weights);
		end if;
	END;			
$$ LANGUAGE plpgsql;	
--select array_multiply()



alter function weighted_av set search_path=hsrr,public;