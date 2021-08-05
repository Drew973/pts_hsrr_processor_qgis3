set search_path to hsrr,public;

drop view if exists hsrr.pieces;

create view hsrr.pieces as

with p as(
select hsrr.requested.sec,reversed,xsp,meas_len,generate_series(0,cast(meas_len as numeric),100) as s_ch
from hsrr.requested inner join network on hsrr.requested.sec=network.sec)
,f as (select *,coalesce(lead(s_ch) over(partition by sec,reversed,xsp order by s_ch),meas_len)::numeric as e_ch from p order by sec,s_ch)

select 
row_number() over (order by sec,reversed,xsp,s_ch)
,sec,reversed,xsp,
s_ch,
e_ch,
numrange(s_ch,e_ch) as rg,

case when reversed then get_line(sec,e_ch,cast(s_ch as float)) when not reversed then get_line(sec,cast(s_ch as float),e_ch) end
as geom										   
	from f where s_ch!=e_ch;


select * from pieces