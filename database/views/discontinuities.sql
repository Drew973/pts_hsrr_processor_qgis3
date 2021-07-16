drop view if exists discontinuities cascade;


create view discontinuities as

select run,f_line,s_ch,ps,a_ps,p,row_number() over (order by f_line) from
(
select run,f_line,s_ch,ps_text::sec_rev[] as ps,e_point as p,(select ps_text::sec_rev[] as a_ps from readings as r where r.run=readings.run and r.f_line=readings.f_line+1) from readings --different to next ps
where not ps_text::sec_rev[]&&(select ps_text::sec_rev[] from readings as r where r.run=readings.run and r.f_line=readings.f_line+1)
union
select run,f_line,s_ch,ps_text::sec_rev[] as ps,s_point,(select ps_text::sec_rev[] from readings as r where r.run=readings.run and r.f_line=readings.f_line-1) from readings --different to last ps
where not ps_text::sec_rev[]&&(select ps_text::sec_rev[] from readings as r where r.run=readings.run and r.f_line=readings.f_line-1)
)a

where not (cardinality(ps)=0 and cardinality(ps)=0);
