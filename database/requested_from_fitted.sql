set search_path to hsrr,public;

delete from requested;

insert into requested(sec,reversed,xsp)
select distinct sec,reversed,xsp from fitted;


select * from requested