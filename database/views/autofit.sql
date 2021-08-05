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
get run chainage of nodes.
get sec_rev from pt and next pt.
insert where sec_rev!=lag(sec_rev)

chainage and position of gaps well known. add last.



*/

