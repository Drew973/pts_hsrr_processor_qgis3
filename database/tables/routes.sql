

create table if not exists hsrr.routes
(
pk serial primary key
,run text references hsrr.run_info(run) on update cascade
,sec text references hsrr.network(sec) on update cascade default 'D' --'D' where run goes off network
,reversed bool generated always as (start_sec_ch>end_sec_ch) STORED
,xsp text
,start_run_ch numeric(7,3) default 0--route chainage in km
,end_run_ch numeric(7,3) default 0--route chainage in km where leaves section
,note text
,start_sec_ch numeric(7,3) default 0
,end_sec_ch numeric(7,3) default 0
);


create index on hsrr.routes(sec);
create index on hsrr.routes(reversed);
create index on hsrr.routes(xsp);
create index on hsrr.routes(run);
create index on hsrr.routes(hsrr.to_numrange(start_run_ch,end_run_ch,'[]'));