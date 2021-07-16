CREATE OR REPLACE FUNCTION array_distinct(a anyarray) 
RETURNS anyarray AS $$
	BEGIN
		return array(select distinct unnest(a));
	END;			
$$ LANGUAGE plpgsql;


--returns duplicated elements
CREATE OR REPLACE FUNCTION array_duplicates(a anyarray) 
RETURNS anyarray AS $$
	BEGIN
		return array(select unnest from unnest(a) group by unnest having count(unnest)>1);
	END;			
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION array_min(anyarray) RETURNS anyelement AS
'SELECT min(i) FROM unnest($1) i' LANGUAGE sql IMMUTABLE;


CREATE OR REPLACE FUNCTION array_max(anyarray) RETURNS anyelement AS
'SELECT max(i) FROM unnest($1) i' LANGUAGE sql IMMUTABLE;


DROP FUNCTION if exists array_multiply(anyarray,anyarray);

--multiplies a[i] by b[i]. Does not check lengths.
--not matrix multiplication
CREATE OR REPLACE FUNCTION array_multiply(a anyarray,b anyarray) 
RETURNS anyarray AS $$
	 BEGIN	
	 	return array(select unnest(a) * unnest(b));
	END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION array_mean(a anyarray) 
RETURNS anyelement AS $$
	 BEGIN	
	 	return AVG(unnest) from unnest(a);
	END;			
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION array_sort_asc(a anyarray) RETURNS anyarray AS
'SELECT array(select unnest from unnest(a) order by unnest asc)' LANGUAGE sql IMMUTABLE;
						   
											   
CREATE OR REPLACE FUNCTION array_sort_desc(a anyarray) RETURNS anyarray AS
'SELECT array(select unnest from unnest(a) order by unnest desc)' LANGUAGE sql IMMUTABLE;											   
											   

CREATE OR REPLACE FUNCTION array_intersect(anyarray, anyarray)
  RETURNS anyarray
  language sql
as $FUNCTION$
    SELECT ARRAY(
        SELECT UNNEST($1)
        INTERSECT
        SELECT UNNEST($2)
    );
$FUNCTION$;


CREATE OR REPLACE FUNCTION array_sum(a anyarray) 
RETURNS anyelement AS $$
	 BEGIN	
	 	return sum(b) from unnest(a) b;
	END;			
$$ LANGUAGE plpgsql;


--return elememts before i where value=a[i]
CREATE OR REPLACE FUNCTION previous_instances(a anyarray, i int) 
RETURNS anyarray AS $$
	 BEGIN	
	 	return array(select unnest from unnest(a[0:i-1]) where unnest=a[i]);
	END;			
$$ LANGUAGE plpgsql;	


--clump elements within tol together. returns array of arraye

CREATE OR REPLACE FUNCTION array_cluster(a numeric[],tol numeric) 
RETURNS numeric[][] AS $$
	Declare
		gaps numrange[];

	 BEGIN	
	 	return null;
		--unnest from unnest(a);
			
		raise notice 'gaps:%',gaps;
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
											
											
