create table section_changes
(
pk serial primary key
,run text references run_info(run) on update cascade on delete cascade
,sec text--next section.can be null where run goes off network
,reversed bool--direction of next section
,xsp text--xsp of next sect section
,ch float--route chainage of node in km
,geom geometry
);



