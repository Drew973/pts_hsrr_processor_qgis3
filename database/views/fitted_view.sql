drop view if exists fitted_view;


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