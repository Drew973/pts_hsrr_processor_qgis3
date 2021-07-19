set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION hsrr.refit(rn varchar) 
	RETURNS void AS $$
	
	BEGIN
	delete from hsrr.fitted where run=rn;
	

	insert into hsrr.fitted(sec,reversed,xsp,run,f_line,vect,s_ch,e_ch,rl)
	
	select
	sec
	,reversed
	,xsp
	,hsrr.routes.run
	,f_line
	,vect
	,meas_sec_ch(sec,s_point) as s_ch
	,meas_sec_ch(sec,e_point) as e_ch
	,rl
	from hsrr.routes inner join hsrr.readings on hsrr.readings.run=rn and hsrr.routes.s_line<=hsrr.readings.f_line and hsrr.readings.f_line<=hsrr.routes.e_line and hsrr.routes.run=rn;
	
	update fitted set rg=int4range(least(s_ch,e_ch)::int,greatest(s_ch,e_ch)::int,'[]') where run=rn;
	
	END;			
$$ LANGUAGE plpgsql;


alter function hsrr.refit(rn varchar) set search_path=hsrr,public;







CREATE OR REPLACE FUNCTION refit() 
	RETURNS void AS $$
	
	BEGIN
	delete from fitted;
	
	with a as(
		select
		routes.run
		,readings.pk as readings_pk
		,sec
		,reversed
		,xsp
		,vect
		,meas_sec_ch(sec,s_point) as sec_ch_s
		,meas_sec_ch(sec,e_point) as sec_ch_e
		,rl
		from routes inner join readings on readings.run=routes.run and numrange(readings.s_ch::numeric,readings.e_ch::numeric)&&numrange(routes.s_ch::numeric,routes.e_ch::numeric)
	)
	insert into fitted(run,readings_pk,sec,reversed,xsp,vect,sec_ch_s,sec_ch_e,rl,rg)
	select run,readings_pk,sec,reversed,xsp,vect,sec_ch_s,sec_ch_e,rl,numrange(least(sec_ch_s,sec_ch_e)::numeric,greatest(sec_ch_s,sec_ch_e)::numeric) from a;
	
	END;			
$$ LANGUAGE plpgsql;


alter function hsrr.refit() set search_path=hsrr,public;





--refit run. approx 60ms. 17/s
CREATE OR REPLACE FUNCTION hsrr.refit(sect varchar,rev bool,xs varchar) 
	RETURNS void AS $$
	
	BEGIN
	delete from hsrr.fitted where sec=sect and reversed=rev and xsp=xs;
	

	insert into hsrr.fitted(sec,reversed,xsp,run,f_line,vect,s_ch,e_ch,rl,rg)
	
	select sec,reversed,xsp,run,f_line,vect,s_ch,e_ch,rl,int4range(least(s_ch,e_ch)::int,greatest(s_ch,e_ch)::int,'[]')
	from
	(select
	sec
	,reversed
	,xsp
	,routes.run as run
	,f_line
	,vect
	,meas_sec_ch(sec,s_point) as s_ch
	,meas_sec_ch(sec,e_point) as e_ch
	,rl
	from routes inner join readings on sec=sect and reversed=rev and xsp=xs and routes.s_line<=hsrr.readings.f_line and readings.f_line<=routes.e_line)a;
		
	END;			
$$ LANGUAGE plpgsql;
alter function hsrr.refit(sect varchar,rev bool,xs varchar) set search_path=hsrr,public;

/*

delete from fitted;

insert into fitted(sec,reversed,xsp,run,readings_pk,vect,sec_ch_s,sec_ch_e,rl)

select
sec
,reversed,xsp,routes.run,readings.pk
,vect
--case when reversed then...,readings.s_ch-routes.s_ch+start_sec_ch as sec_ch_s
--,readings.e_ch-routes.s_ch+start_sec_ch as sec_ch_e
,meas_sec_ch(sec,st_startPoint(vect)) as sec_ch_s
,meas_sec_ch(sec,st_endPoint(vect)) as sec_ch_e
,rl

from readings left join routes on readings.run=routes.run and rg&&numrange(routes.s_ch::numeric,routes.e_ch::numeric)
order by readings.run,readings.s_ch,sec_ch_s desc;
update fitted set rg=numrange(least(sec_ch_s::numeric,sec_ch_e::numeric),greatest(sec_ch_s::numeric,sec_ch_e::numeric));

*/
