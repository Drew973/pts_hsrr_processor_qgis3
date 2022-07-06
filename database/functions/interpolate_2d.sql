

--linear interpolation between 2 points (x1,y1) and (x2,y2)
CREATE OR REPLACE FUNCTION hsrr.interpolate_2d(x numeric,x1 numeric,y1 numeric,x2 numeric,y2 numeric) 
RETURNS numeric AS $$
		Declare
			m numeric = (y2-y1)/(x2-x1);
			c numeric = y1-m*x1;
        BEGIN	
			return m*x+c;
		END		
$$
LANGUAGE plpgsql;


--select hsrr.interpolate_2d(0,0,0,2,2)--should be 0
--select hsrr.interpolate_2d(1,0,0,2,2)-- should be 1
--select hsrr.interpolate_2d(2,0,0,2,2)-- should be 2
--select hsrr.interpolate_2d(1,0,0,2,-2)-- should be -1