
set search_path to hsrr,public;


drop type if exists weighted_val cascade;

create type weighted_val as
(
val numeric
,weight numeric
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