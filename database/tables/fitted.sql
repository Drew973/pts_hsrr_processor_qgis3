

create table if not exists hsrr.fitted
(
pk serial
,run text--foreign key? unnecesary as generated from routes and routes has fk on run.
,sec text--foreign key? unnecesary as generated from routes and routes has fk on sec.
,reversed bool generated always as (s_ch>e_ch) STORED
,xsp text
,vect geometry('linestring',27700)--only used for display
,rl numeric
,s_ch numeric--start section chainage
,e_ch numeric--end section chainage
,readings_pk int--only used for display
,rg numrange generated always as (hsrr.to_numrange(s_ch,e_ch,'()')) stored
);


create index if not exists fitted_sec on hsrr.fitted(sec);
create index if not exists fitted_rev on hsrr.fitted(reversed);
create index if not exists fitted_rg on hsrr.fitted(rg);