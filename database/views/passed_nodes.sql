drop view if exists passed_nodes cascade;

create view passed_nodes as

with nodes as(
select st_startPoint(geom) as pt from network where not geom is null
union
select st_endPoint(geom) from network where not geom is null
)

,a as (select pt,run,hsrr.pt_to_run_ch(run,pt) as ch from nodes inner join readings on st_dwithin(vect,pt,50))

--select distinct on (run,ch) run,ch,pt,row_number() over(order by run,ch) from a;
select run,ch,pt,row_number() over(order by run,ch) from a;

select * from passed_nodes;