insert into requested(sec,reversed,xsp)
select distinct sec,reversed,xsp from section_changes;


select * from requested