set search_path to hsrr,public;

set search_path to hsrr,public;

drop view if exists gaps cascade;

create view gaps as

with a as (select run,e_ch as ch,st_endPoint(vect) as pt,vect,lead(vect) over (partition by run order by s_ch) from readings)--next null--ends
,b as (select run,s_ch as ch,st_startPoint(vect) as pt,vect,lag(vect) over (partition by run order by s_ch) from readings)
,c as (
	select run,ch,pt from a where lead is null or not st_dwithin(st_endpoint(vect),st_startPoint(lead),5)
	union
	select run,ch,pt from b where lag is null or not st_dwithin(st_startpoint(vect),st_endPoint(lag),5)
	)

--select run,ch,ST_ClosestPoint(geom,pt) as pt,row_number() over(order by run,ch) from c inner join network on st_dwithin(pt,geom,20);
select run,ch,pt,row_number() over(order by run,ch) from c;
