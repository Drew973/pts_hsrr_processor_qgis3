set search_path to hsrr,public;


create table if not exists fitted
(
pk serial
,run text
,sec text
,reversed bool
,xsp text
,vect geometry
,rl numeric
,s_ch numeric
,e_ch numeric
,readings_pk int
,rg numrange
);