set search_path to hsrr,public;

drop view if exists possible_sections;

create view possible_sections as

with n as (
	select sec,False as reversed,geom from network where has_forward
	union
	select sec,True,st_reverse(geom) from network where has_reverse
)

,a as (
select run,sec,reversed,pt_to_run_ch(run,st_startPoint(n.geom)) as ch,n.geom from run_geom inner join n on
st_dwithin(run_geom.geom,n.geom,40)
and vectors_align(n.geom,run_geom.geom)
)

select row_number() over(order by run,ch),run,sec,reversed,ch,geom from a;
		   
		   