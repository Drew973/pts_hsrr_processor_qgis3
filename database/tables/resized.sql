set search_path to hsrr,public;


create table if not exists resized
(
pk serial
,sec text
,reversed bool
,xsp text
,s_ch numeric
,e_ch numeric
,vals text
,rl numeric
,geom geometry('LineString',27700)
);


alter table hsrr.resized add column rg numrange;
create index on hsrr.resized(rg);
