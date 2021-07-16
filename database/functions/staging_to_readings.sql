CREATE OR REPLACE FUNCTION hsrr.staging_to_readings() 
	RETURNS void AS $$
	
	BEGIN
	
		update hsrr.staging set start_point=St_Transform(ST_SetSRID(ST_makePoint(start_lon,start_lat),4326),27700);
		update hsrr.staging set end_point=St_Transform(ST_SetSRID(ST_makePoint(end_lon,end_lat),4326),27700);

		insert into hsrr.readings(run,f_line,t,raw_ch,rl,s_point,e_point,vect,s_ch,e_ch)
		select run,
		f_line,
		to_timestamp(replace(ts,' ',''),'dd/mm/yyyyHH24:MI:ss'),
		raw_ch,--raw_ch*1000
		rl,
		start_point
		,end_point
		,st_makeLine(start_point,end_point)
		,(f_line-(select min(f_line) from staging as s where s.run=staging.run))*0.1--s_ch in km
		,0.1+(f_line-(select min(f_line) from staging as s where s.run=staging.run))*0.1--e_ch in km
		--update readings set rg = numrange(s_ch::numeric,e_ch::numeric);

		from hsrr.staging;

		delete from hsrr.staging;

	END;
	
$$ LANGUAGE plpgsql;

