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



