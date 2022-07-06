
--update hsrr.section_changes set reversed = start_sec_ch>end_sec_ch;

--insert into hsrr.requested(sec,reversed,xsp)
--select distinct sec,reversed,xsp from hsrr.section_changes where not sec='D';



insert into requested(sec,reversed,xsp)
select distinct sec,reversed,xsp from section_changes;


select * from requested