
-- function to calculate section chainage given ch and 2 ch,sec_ch pairs in same section.
--for use where gps not good enough to find nearest point on section.
--straight line fit between sec_ch and ch. 
--when ch=s_ch sec_ch=start_sec_ch. when ch=e_ch sec_ch=end_sec_ch.
CREATE OR REPLACE FUNCTION ch_to_sec_ch(ch float,s_ch float,e_ch float,start_sec_ch float,end_sec_ch float) 
RETURNS float AS $$
Declare
	m float=(end_sec_ch-start_sec_ch)/(e_ch-s_ch);
	c float=end_sec_ch-m*e_ch;
	
	BEGIN
		return m*ch+c;
		
	END;			
$$ LANGUAGE plpgsql;