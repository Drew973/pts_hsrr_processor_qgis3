set search_path to hsrr,public;


create table if not exists hsrr.section_changes
(
pk serial primary key
,run text references run_info(run) on update cascade
,sec text references network(sec) on update cascade default 'D' --'D' where run goes off network
,reversed bool
,xsp text
,ch numeric--route chainage in km
,e_ch numeric--route chainage in km where leaves section
,note text
,start_sec_ch numeric--route
,end_sec_ch numeric
,pt geometry('point')
);



create index on hsrr.section_changes(sec);
create index on hsrr.section_changes(reversed);
create index on hsrr.section_changes(xsp);
create index on hsrr.section_changes(run);
create index on hsrr.section_changes(hsrr.to_numrange(ch,e_ch));