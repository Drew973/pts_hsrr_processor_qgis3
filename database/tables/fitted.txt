set search_path to hsrr,public;


create table if not exists fitted
(
pk serial primary key
,run varchar references hsrr.run_info(run) on delete cascade on update cascade
,readings_pk int references readings(pk) on delete cascade on update cascade
,sec varchar references network(sec) on delete cascade on update cascade
,reversed bool
,xsp varchar
,vect geometry('linestring',27700)
,sec_ch_s float
,sec_ch_e float
,rl float
,rg numrange
);

create index if not exists vect_ind on hsrr.fitted using gist(vect);
create index if not exists rg_ind on hsrr.fitted using gist(rg);
create index if not exists sec_ind on hsrr.fitted(sec);
create index if not exists xsp_ind on hsrr.fitted(xsp);
create index if not exists rev_ind on hsrr.fitted(reversed);


