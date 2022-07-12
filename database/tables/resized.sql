

create table if not exists hsrr.resized
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



create index if not exists resized_rg on hsrr.resized(hsrr.to_numrange(s_ch,e_ch,'()'));