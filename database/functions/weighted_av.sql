
DROP TYPE IF EXISTS hsrr.weighted_val cascade;

CREATE TYPE hsrr.weighted_val as
(
val numeric
,weight numeric
);


--sum(value*weight)/sum(weight)
--will give div by 0 error when sum of weights is 0. probably a good thing

CREATE OR REPLACE FUNCTION hsrr.weighted_av(vals hsrr.weighted_val[]) 
RETURNS numeric AS $$
	 BEGIN	
		return sum((unnest).weight*(unnest).val)/sum((unnest).weight) from unnest(vals);
	END;			
$$ LANGUAGE plpgsql;	


--select weighted_av('{"(0,5)","(10,5)"}'::weighted_val[]);