drop view if exists resized_view;

create or replace view resized_view as
select
row_number() over (order by sec,reversed,xsp,s_ch)
,sec
,reversed
,xsp
,s_ch
,e_ch
,lengths
,vals
,hsrr.weighted_av(lengths::int[],vals) as rl
,hsrr.get_line(sec,least(s_ch,e_ch),greatest(s_ch,e_ch)) as geom
from
(select p.sec,p.reversed,p.xsp,p.s_ch,p.e_ch,array_agg(upper(p.rg*fitted.rg)-lower(p.rg*fitted.rg)) as lengths,array_agg(rl) as vals from (select sec,reversed,xsp,(gp).s_ch,(gp).e_ch,int8range(least((gp).s_ch,(gp).e_ch)::int,greatest((gp).s_ch,(gp).e_ch)::int) as rg
from (select sec,reversed,xsp,get_pieces(sec) as gp from requested)a)p
left join hsrr.fitted_view as fitted on p.sec=fitted.sec and p.reversed=fitted.reversed and p.xsp=fitted.xsp and p.rg&&fitted.rg
group by p.sec,p.reversed,p.xsp,p.s_ch,p.e_ch)a;


ALTER VIEW resized_view SET SCHEMA hsrr