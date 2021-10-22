set search_path to hsrr,public;


/*

nearest point on readings


drop view if exists passed_nodes cascade;

create view passed_nodes as

with nodes as(
select st_startPoint(geom) as pt from network where not geom is null
union
select st_endPoint(geom) from network where not geom is null
)

,a as (select ST_ClosestPoint(vect,pt) as pt,run,s_ch,e_ch,s_ch+(e_ch-s_ch)*st_lineLocatePoint(vect,pt) as ch from nodes inner join readings on st_dwithin(vect,pt,50))

--select distinct on (run,ch) run,ch,pt,row_number() over(order by run,ch) from a;
select run,ch::numeric,pt,row_number() over(order by run,ch) from a where s_ch<ch and ch<e_ch;


select * from passed_nodes;

*/



drop view if exists passed_nodes cascade;

create view passed_nodes as

with nodes as(
select st_startPoint(geom) as pt from network where not geom is null
union
select st_endPoint(geom) from network where not geom is null
)

,a as (select pt,run,s_ch,e_ch,s_ch+(e_ch-s_ch)*st_lineLocatePoint(vect,pt) as ch from nodes inner join readings on st_dwithin(vect,pt,50))

--select distinct on (run,ch) run,ch,pt,row_number() over(order by run,ch) from a;
select run,ch::numeric,pt,row_number() over(order by run,ch) from a where s_ch<ch and ch<e_ch;


select * from passed_nodes;