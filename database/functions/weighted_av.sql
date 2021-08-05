
set search_path to hsrr,public;



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




create type weighted_val
(
val numeric
weight numeric
);



--sum(value*weight)/sum(weigt)
--will give div by 0 error when sum of weights is 0. probably good thing

CREATE OR REPLACE FUNCTION weighted_av(vals weighted_val[]) 
RETURNS numeric AS $$
	-- declare weight_sum numeric=sum((unnest).weight) from unnest(vals);
	 BEGIN	
		return sum((unnest).weight*(unnest).val)/sum((unnest).weight) from unnest(vals);
	END;			
$$ LANGUAGE plpgsql;	


alter function weighted_av(weighted_val[]) set search_path=hsrr,public;

--select weighted_av('{"(0,5)","(10,5)"}'::weighted_val[]);