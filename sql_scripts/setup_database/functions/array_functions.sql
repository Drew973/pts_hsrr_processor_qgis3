CREATE OR REPLACE FUNCTION array_distinct(anyarray) 
RETURNS anyarray AS $$
	BEGIN
		return array(select distinct unnest(arr));
	END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION array_min(anyarray) RETURNS anyelement AS
'SELECT min(i) FROM unnest($1) i' LANGUAGE sql IMMUTABLE;


CREATE OR REPLACE FUNCTION array_max(anyarray) RETURNS anyelement AS
'SELECT max(i) FROM unnest($1) i' LANGUAGE sql IMMUTABLE;


CREATE OR REPLACE FUNCTION array_multiply(a numeric[],b numeric[]) 
RETURNS numeric[] AS $$
	 BEGIN	
	 	return array(select unnest(a) * unnest(b));
	END;			
$$ LANGUAGE plpgsql;															   


CREATE OR REPLACE FUNCTION array_multiply(a int[],b int[]) 
RETURNS int[] AS $$
	 BEGIN	
	 	return array(select unnest(a) * unnest(b));
	END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION array_mean(a float[]) 
RETURNS float AS $$
	DECLARE
		s float=sum(b) from unnest(a) b;
	 BEGIN	
	 	return s/cardinality(a);
	END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION array_sort_asc(a anyarray) RETURNS anyarray AS
'SELECT array(select unnest from unnest(a) order by unnest asc)' LANGUAGE sql IMMUTABLE;
						   
											   
CREATE OR REPLACE FUNCTION array_sort_desc(a anyarray) RETURNS anyarray AS
'SELECT array(select unnest from unnest(a) order by unnest desc)' LANGUAGE sql IMMUTABLE;											   
											   
CREATE OR REPLACE FUNCTION array_sum(a int[]) 
RETURNS int AS $$
	 BEGIN	
	 	return sum(b) from unnest(a) b;
	END;			
$$ LANGUAGE plpgsql;
									 

--make array into ranges of values separated by dist		
--[] type range. upper will be 1 too high

CREATE OR REPLACE FUNCTION array_cluster_int(a int[],dist int) 
RETURNS int4range[] AS $$
	Declare
	v int;
	sorted int[]=array_sort_asc(a);
	prev int=sorted[1];
	s int=sorted[1];
	r int4range[];					 
				
									 
	BEGIN
		if cardinality(a)=1 then 
			r= r||int4range(a[1],a[1],'[]');--need [] to not be empty
			return r;
		end if;
								   
	
		FOREACH v in array sorted loop
			--raise notice 's: %', s;
			if v-prev>dist then
				r=r||int4range(s,prev,'[]');
				s=v;
			end if;
			prev=v;
		end loop;
									 
			r=r||int4range(s,v,'[]');							 
				 
	return r;
	END;			
$$ LANGUAGE plpgsql;											
											
											
