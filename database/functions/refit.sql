

/*
	refit everything
	5-10s for all area 12.
*/
CREATE OR REPLACE FUNCTION hsrr.refit() 
	RETURNS void AS $$


	delete from hsrr.fitted;

	insert into hsrr.fitted(run,sec,xsp,vect,rl,s_ch,e_ch)

	select 
	readings.run,sec,routes.xsp,vect,rl

	,greatest(hsrr.interpolate_2d(s_ch,start_run_ch,start_sec_ch,end_run_ch,end_sec_ch),0) as s
	,least(hsrr.interpolate_2d(e_ch,start_run_ch,start_sec_ch,end_run_ch,end_sec_ch),hsrr.meas_len(sec)::numeric) as e

	from hsrr.routes inner join hsrr.readings on
	hsrr.to_numrange(s_ch,e_ch,'[]')&&hsrr.to_numrange(start_run_ch,end_run_ch,'()')
	and routes.run = readings.run
	and not sec='D'
	
	$$ language sql;

--select hsrr.refit();


/*
refit section and xsp
*/
CREATE OR REPLACE FUNCTION hsrr.refit(sect text,xs text) 
	RETURNS void AS $$


	delete from hsrr.fitted where sec=sect and xsp=xs;

	insert into hsrr.fitted(run,sec,xsp,vect,rl,s_ch,e_ch)

	select 
	readings.run,sec,routes.xsp,vect,rl

	,greatest(hsrr.interpolate_2d(s_ch,start_run_ch,start_sec_ch,end_run_ch,end_sec_ch),0) as s
	,least(hsrr.interpolate_2d(e_ch,start_run_ch,start_sec_ch,end_run_ch,end_sec_ch),hsrr.meas_len(sec)::numeric) as e

	from hsrr.routes inner join hsrr.readings on
	hsrr.to_numrange(s_ch,e_ch,'[]')&&hsrr.to_numrange(start_run_ch,end_run_ch,'()')
	and routes.run = readings.run and sec=sect and xsp=xs
	and not sec='D'
	
	$$ language sql;
