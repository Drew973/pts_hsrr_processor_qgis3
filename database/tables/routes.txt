--drop table if exists hsrr.routes cascade;

create table if not exists hsrr.routes(
sec varchar references network(sec) ON DELETE CASCADE ON UPDATE CASCADE
,reversed bool
,xsp varchar
,run varchar references hsrr.run_info(run) ON DELETE CASCADE ON UPDATE CASCADE
,s_ch float
,e_ch float
,note varchar
,start_sec_ch float
,end_sec_ch float
,pk serial primary key--needs primary key for qsqltablemodel to work properly
);

create index if not exists routes_run on hsrr.routes(run);
