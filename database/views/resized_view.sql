set search_path to hsrr,public;



drop view if exists resized_view cascade;

create view resized_view as 
select p.row_number,p.sec,p.reversed,p.xsp,p.s_ch,p.e_ch
--,'values '||array_agg((f.rl,upper(p.rg*f.rg)-lower(p.rg*f.rg))::weighted_val)::text||' ' as vals

,array_agg(upper(p.rg*f.rg)-lower(p.rg*f.rg) order by upper(p.rg*f.rg)-lower(p.rg*f.rg))::text as lengths
,array_agg(rl  order by upper(p.rg*f.rg)-lower(p.rg*f.rg))::text as vals
								  
,weighted_av(array_agg((f.rl,upper(p.rg*f.rg)-lower(p.rg*f.rg))::weighted_val)) as rl
													
,p.geom													
from pieces as p left join fitted_view as f 
on p.rg&&numrange(least(f.s_ch,f.e_ch),greatest(f.s_ch,f.e_ch)) and p.sec=f.sec and f.reversed=p.reversed and p.xsp=f.xsp
group by p.row_number,p.sec,p.reversed,p.xsp,p.s_ch,p.e_ch,p.geom;

select * from resized_view;