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



CREATE OR REPLACE FUNCTION hsrr.refit() 
	RETURNS void AS $$
	
	BEGIN
	delete from fitted;
	
	insert into fitted(sec,reversed,xsp,run,f_line,vect,s_ch,e_ch,rl)
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
	from hsrr.routes inner join hsrr.readings on hsrr.readings.run=hsrr.routes.run and hsrr.routes.s_line<=hsrr.readings.f_line and hsrr.readings.f_line<=hsrr.routes.e_line;
	
	update fitted set rg=int4range(least(s_ch,e_ch)::int,greatest(s_ch,e_ch)::int,'[]');
	
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
