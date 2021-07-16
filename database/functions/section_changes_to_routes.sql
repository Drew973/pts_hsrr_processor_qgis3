

delete from routes;

with a as (select sec,reversed,xsp,run,ch,lead(ch) over (partition by run order by ch) from section_changes)
insert into routes(sec,reversed,xsp,run,s_ch,e_ch)
select sec,reversed,xsp,run,ch,lead from a where sec in (select sec from network)




