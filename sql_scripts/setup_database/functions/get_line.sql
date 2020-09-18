
--part of linestring  from start_ch to end_ch. len=noninal length. chainages in terms of nominal length

CREATE OR REPLACE FUNCTION make_line(L geometry('linestring'),len float,start_ch float,end_ch float) 
RETURNS geometry('linestring') AS $$
		declare
			f1 float;
			f2 float;
        BEGIN	
				f1=start_ch/len;
				f2=end_ch/len;
				
				if f1<0 then
					f1=0;
				end if;
				
				if f1>1 then
					f1=1;
				end if; 

				if f2>1 then
					f2=1;
				end if; 

				if f2<0 then
					f2=0;
				end if; 
				
				if f2>f1 then
					return ST_LineSubstring(L,f1,f2);
				else
					return st_reverse(ST_LineSubstring(L,f2,f1));
				end if;
													   
		END;			
$$ LANGUAGE plpgsql;
													   

--returns linestring from start_ch to end_ch of section, start_ch and end_ch in terms of meas_len.
													   					
CREATE OR REPLACE FUNCTION get_line(sect varchar,start_ch float,end_ch float) 
RETURNS geometry AS $$
		declare g geometry=geom from network where sec=sect;
        BEGIN	
				return make_line(g,meas_len(sect),start_ch,end_ch);
		END;			
$$ LANGUAGE plpgsql;						
