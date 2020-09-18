--puts all possible sections into routes. 

drop view if exists pos cascade;

drop view if exists a cascade;
create temp view a as select run,f_line,unnest(possible_secs(pt,vect)) as s_r from r;
													   
create temp view b as select run,f_line,split_part(s_r,'#',1)  as sec,cast(split_part(s_r,'#',2) as bool) as rev from a;
														 

delete from routes;

insert into routes(sec,reversed,run,s,e,note)
select sec,
rev,
run,
lower(unnest(array_cluster_int(array_agg(f_line),50))) as s,
upper(unnest(array_cluster_int(array_agg(f_line),50))) as e,
'auto'							   
from b group by run,sec,rev;

							   
							   
							   
select * from b;
							   
							   --25s