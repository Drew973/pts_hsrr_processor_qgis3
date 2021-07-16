--where node passed
---where turned off network
--either side of gap between readings. where gap between reading and next reading or gap between reading and last reading.



set search_path to hsrr,public;


delete from section_changes;

--gap between reading and next reading
with a as (select run,e_ch,e_point,vect,lead(vect) over (partition by run order by s_ch) from readings)
insert into section_changes(run,ch,geom)
select run,e_ch,e_point from a where lead is null or not st_dwithin(vect,lead,10);


--gap between reading and last reading
with a as (select run,s_ch,s_point,vect,lag(vect) over (partition by run order by s_ch) from readings)
insert into section_changes(run,ch,geom)
select run,s_ch,s_point from a where lag is null or not st_dwithin(vect,lag,10);


--passes node
insert into section_changes(run,ch,geom)
select run,s_ch+0.1*st_lineLocatePoint(vect,p) as ch,st_closestPoint(vect,p) as p
from readings inner join nodes on st_dwithin(vect,p,15) and st_lineLocatePoint(vect,p)>0 and st_lineLocatePoint(vect,p)<1;


--insert into section_changes(run,ch,geom)
--select run,s_ch,p from discontinuities;

update section_changes set sec = (sr_between_points(geom,(select geom as next_geom from section_changes as s where s.run=section_changes.run and s.ch>section_changes.ch order by ch limit 1))).sec;
update section_changes set reversed = (sr_between_points(geom,(select geom as next_geom from section_changes as s where s.run=section_changes.run and s.ch>section_changes.ch order by ch limit 1))).rev;
