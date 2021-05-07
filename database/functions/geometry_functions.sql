CREATE OR REPLACE FUNCTION split_geom(geom geometry('linestring'),positions float[]) 
RETURNS geometry('linestring')[] AS $$
        BEGIN	
			return array(select ST_LineSubstring(geom,unnest,coalesce(lead(unnest) over(order by unnest),1)) from unnest(positions));						   
		END;			
$$ LANGUAGE plpgsql;
