
--part of linestring  from start_ch to end_ch. len=noninal length. chainages in terms of nominal length


CREATE OR REPLACE FUNCTION make_line(L geometry('linestring'),rg numeric,len numeric=null) 
RETURNS geometry('linestring') AS $$
		declare
			f1 float;
			f2 float;
        BEGIN	
				if len is null then
					len=st_length(L);
				end if;
		
				f1 = clamp(start_ch/len,0,1);
				f2 = clamp(end_ch/len,0,1);
				
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
		declare g geometry=geom from hsrr.network where sec=sect;
        BEGIN	
			return make_line(L:=g,len:=meas_len(sect),start_ch:=start_ch,end_ch:=end_ch);
			--g=make_line(L:=g,len:=meas_len(sect),start_ch:=start_ch,end_ch:=end_ch);
			--raise notice 'get line(sect=%,start_ch=%,end_ch=%',sect,start_ch,end_ch;
			--return g;
		END;			
$$ LANGUAGE plpgsql;	


--returns section geometry from closest point to start_pt to closest point of end_pt									   					
CREATE OR REPLACE FUNCTION get_line(sect varchar,start_pt geometry,end_pt geometry) 
RETURNS geometry AS $$
		declare g geometry=geom from network where sec=sect;
		s_ch float= st_lineLocatePoint(g,start_pt)*st_length(g);
		e_ch float= st_lineLocatePoint(g,end_pt)*st_length(g);
		
        BEGIN	
				return make_line(g,s_ch,e_ch);
		END;			
$$ LANGUAGE plpgsql;						


alter function get_line(varchar,geometry,geometry) set search_path to hsrr,public;
alter function get_line(varchar,float,float) set search_path to hsrr,public;
