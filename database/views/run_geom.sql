drop view if exists run_geom cascade;

create view run_geom as
with a as (select run, ST_LineMerge(ST_Collect(vect)) as geom from readings group by run)
,b as(select run,(st_dump(geom)).geom from a)
select row_number() over (order by run),run,geom from b;