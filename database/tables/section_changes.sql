set search_path to hsrr,public;


create table if not exists section_changes
(
pk serial primary key
,run text references run_info(run) on update cascade
,sec text references network(sec) on update cascade default 'D' --'D' where run goes off network
,reversed bool
,xsp text
,ch numeric--route chainage in km
,note text
,start_sec_ch numeric--route
,end_sec_ch numeric
,pt geometry('point')
--,UNIQUE(run,ch)
);



