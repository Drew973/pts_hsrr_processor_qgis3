

--want 1 sec per point,2 where overlap

---update r set ps=ps(pt,vect,0.833,1,1,0);
--update r set ps_text=cast(ps as varchar);	

drop view if exists a;

create temp view a as
select run,ps[1] as p,unnest(array_cluster_int(array_agg(f_line),2)) from r group by run,ps[1];
										  

delete from routes where note='auto';						  
insert into routes(run,sec,reversed,s,e,note) 										  
select run,(p).sec,(p).rev,lower(unnest),upper(unnest),'auto' from a where not (p).sec is null;		  
											   





