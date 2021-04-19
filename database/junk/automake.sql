drop table if exists ps cascade;
create table ps as select ref,cast(ch as int),possible_secs(pt,vect),pt from joined;
create index on ps(possible_secs);
create index on ps(ref);


drop view if exists definite cascade;
create view definite as select ref,ch,split_part(possible_secs[1],'#',1) as sec,cast(split_part(possible_secs[1],'#',2) as bool) as reversed from ps where cardinality(possible_secs)=1;

drop view if exists auto_routes;

create view auto_routes as 
select ref,
sec,
reversed,
case when reversed then 'CR1' when not reversed then 'CL1' end as xsp,
lower(unnest(array_cluster_int(array_agg(ch),50))) as s_ch,
upper(unnest(array_cluster_int(array_agg(ch),50))) as e_ch
from definite group by ref,sec,reversed;

--select ref,sec,reversed,better_s_ch(ref,sec,reversed,s_ch),better_s_ch(ref,sec,not reversed,e_ch) from ar order by ref,s_ch; 					   


insert into routes(sec,xsp,ref,s_ch,e_ch,note)
select  sec,
		xsp,
		ref,
		better_s_ch(ref,sec,reversed,s_ch) as s_ch,
		better_e_ch(ref,sec,reversed,e_ch) as e_ch,
		'auto'as note
	from auto_routes 
		where 0=(select count(routes.sec) from routes where routes.sec=auto_routes.sec and routes.xsp=auto_routes.xsp and abs(auto_routes.s_ch-routes.s_ch)<50) --no nearby entry
		and e_ch>s_ch and e_ch-s_ch<meas_len(sec)+30;-- and sanity check


