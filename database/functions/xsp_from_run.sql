set search_path to hsrr,public;

--select * from pieces

create or replace function xsp_from_run(rn text) 
returns void as $$
update section_changes set xsp=case
when upper(run) like '%CL1%' then 'CL1'
when upper(run) like '%LE%' then 'LE'
when upper(run) like '%RE%' then 'RE'
when upper(run) like '%CL2%' then 'RE'
else xsp
end
where run=rn
$$ language sql;

alter function xsp_from_run set search_path=hsrr;

--select *,xsp_from_run(run) from run_info