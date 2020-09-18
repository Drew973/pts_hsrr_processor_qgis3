--estimate of how good fit to sec_dir is. lower is better fit.

CREATE OR REPLACE FUNCTION unlikelyness(s sec_dir,_run varchar,_s int,_e int)
RETURNS float AS $$											 
    declare
		pts geometry[] = array(select pt from r where r.run=_run and _s<=f_line and f_line<=_e);
		geom geometry = geom from network where sec=s.sec;
		dist_sum float = sum(st_distance(geom,pt)) from unnest(pts) as pt; 
		meas_len float = meas_len(s.sec);
		start_gap float = min(meas_sec_ch(s.sec,pt)) from unnest(pts) as pt;--distance between start of section and 1st point
		end_gap float = abs(meas_len-max(meas_sec_ch(s.sec,pt))) from unnest(pts) as pt;--distance between start of section and 1st point
												  
	BEGIN
		return 1*dist_sum/cardinality(pts)+1*(start_gap+end_gap)/meas_len;--1*average distance+20*uncovered fraction of sec
											 
	END;			
$$ LANGUAGE plpgsql;
										 										 
										 
select * from routes	