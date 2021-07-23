set search_path to hsrr,public;


create table section_changes
(
pk serial primary key
,run text references run_info(run) on update cascade on delete cascade
,sec text references network(sec) on update cascade on delete cascade--can be null where run goes off network
,reversed bool
,xsp text
,ch numeric--route chainage in km
,start_sec_ch numeric--route
,end_sec_ch numeric
,pt geometry('point')
);



