CREATE OR REPLACE FUNCTION hsrr.staging_to_readings() 
	RETURNS void AS $$
	
	BEGIN
	
		update hsrr.staging set start_point=St_Transform(ST_SetSRID(ST_makePoint(start_lon,start_lat),4326),27700);
		update hsrr.staging set end_point=St_Transform(ST_SetSRID(ST_makePoint(end_lon,end_lat),4326),27700);

		insert into hsrr.readings(run,f_line,t,raw_ch,rl,s_point,e_point,vect)
		select run,
		f_line,
		to_timestamp(replace(ts,' ',''),'dd/mm/yyyyHH24:MI:ss'),
		raw_ch*1000,
		rl,
		start_point,
		end_point,
		st_makeLine(start_point,end_point)
		from hsrr.staging;

		delete from hsrr.staging;
	END;
	
$$ LANGUAGE plpgsql;