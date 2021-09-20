drop view if exists fitted_view;

/*
create or replace view fitted_view as
select row_number() over (order by run,f_line),sec,reversed,xsp,run,f_line,vect,s_ch,e_ch,rl,int8range(least(s_ch,e_ch)::int,greatest(s_ch,e_ch)::int) as rg from
(select sec
,reversed
,xsp
,routes.run
,f_line
,vect
,hsrr.meas_sec_ch(sec,s_point) as s_ch
,hsrr.meas_sec_ch(sec,e_point) as e_ch
,rl
from hsrr.routes as routes inner join hsrr.readings as readings on readings.run=routes.run and routes.s_line<=readings.f_line and readings.f_line<=routes.e_line)a;
*/



set search_path to hsrr,public;

drop view if exists fitted_view cascade;
create view fitted_view as

with r as (select run,sec,reversed,xsp,start_sec_ch,end_sec_ch,numrange(ch,lead(ch) over (partition by run order by ch)) as rg from section_changes where not sec='D')
		,a as(																	 
		select
		row_number() over (order by r.run,sec,xsp,reversed,s_ch)
		,r.run
		,sec
		,reversed
		,xsp
		,vect
		,rl
		,meas_sec_ch(sec,st_startPoint(vect))::numeric as s_ch
		,meas_sec_ch(sec,st_endPoint(vect))::numeric as e_ch
		,readings.pk as readings_pk	
		from r inner join readings on r.rg&&numrange(s_ch::numeric,e_ch::numeric) and r.run=readings.run)
		select *,numrange(least(s_ch,e_ch),greatest(s_ch,e_ch)) as rg from a;