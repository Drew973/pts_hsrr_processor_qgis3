set search_path to hsrr,public;

drop view if exists section_changes_view;

create view section_changes_view as
with a as (select *,lead(s_ch) over (partition by run order by s_ch) from routes)
, b as (
select run,sec,reversed,xsp,s_ch from a
union
select run,null,null,null,e_ch from a where lead>e_ch or lead is null
)
select run,sec,reversed,xsp,s_ch from b order by run,s_ch;
