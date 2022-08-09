delete from hsrr.resized;



with a as 
(
	select network.sec,reversed,xsp,meas_len,generate_series(0.0,meas_len::numeric,0.1) as s
	from 
		(select sec,reversed,xsp 
		from hsrr.routes group by sec,reversed,xsp
		 ) g
	inner join hsrr.network on g.sec=network.sec
)
	
,b as (select sec,xsp,reversed,
	   case when reversed then least(s+0.1,meas_len::numeric)else s end as start_sec_ch
	   ,case when reversed then s else least(s+0.1,meas_len::numeric) end as end_sec_ch
	   from a)
	   
insert into hsrr.resized(sec,xsp,reversed,s_ch,e_ch,geom)
select sec,xsp,reversed,start_sec_ch,end_sec_ch,hsrr.network_geom(sec,start_sec_ch,end_sec_ch) from b
where start_sec_ch!=end_sec_ch;


select hsrr.process();