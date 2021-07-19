set search_path to hsrr,public;


insert into requested(sec,reversed,xsp)
select distinct sec,reversed,xsp from fitted;


select * from requested