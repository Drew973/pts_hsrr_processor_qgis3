
update routes set s_ch-better_s_ch(ref,sec,False,s_ch) where xsp='CL1';
update routes set e_ch-better_s_ch(ref,sec,True,e_ch) where xsp='CL1';

update routes set e_ch-better_s_ch(ref,sec,True,s_ch) where xsp='CR1';
update routes set e_ch-better_s_ch(ref,sec,False,e_ch) where xsp='CR1';

--returns closest chainage in joined to start of sect and within 50m of a
CREATE OR REPLACE FUNCTION better_s_ch(re varchar,sect varchar,rev bool,a int) 
RETURNS int AS $$
	declare p geometry=case when rev then st_endpoint(geom) from network where sec=sect limit 1
					 wnen not rev then st_startpoint(geom) from network where sec=sect limit 1;
					 
	 BEGIN	
	 	return ch from joined where ref=re and abs(ch-a)<50 and st_dwithin(p,pt,10) order by st_distance(p,pt) limit 1;
	END;			
$$ LANGUAGE plpgsql;