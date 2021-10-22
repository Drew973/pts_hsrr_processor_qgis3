set search_path to hsrr,public;

drop view if exists autofit;

create view autofit as

with a as
(select run,ch,pt from passed_nodes 
union 
select run,ch,pt from gaps)

,b as
(select run
,ch
,hsrr.srs_between_points(pt,lead(pt) over (partition by run order by ch)) as srs
,pt
,st_makeLine(pt,lead(pt) over (partition by run order by ch)) as geom
from a)		
			 
,c as (select *,lag(srs) over (partition by run order by ch) from b)
select run,ch,srs,srs::text as srs_text,geom,pt,row_number() over(order by run,ch) from c where lag[1]!=srs[1];
	
	



/*
with a as (select pk,ch,srs_between_points(pt,lead(pt) over (order by ch)) from section_changes where run ='SEW NB CL1' and note ='auto')
,b as (select *,(srs_between_points[1]).sec,(srs_between_points[1]).rev from a)
update section_changes set sec = b.sec ,reversed = b.rev from b where b.pk=section_changes.pk;

*/

