
update r set ps=ps(pt,vect,0.833,1,1,0) where run=%(run)s;
update r set ps_text=cast(ps as varchar[]) where run=%(run)s;


delete from routes where run=%(run)s and note='auto';						  									   
											   
with a as (select ps[1] as p,unnest(array_cluster_int(array_agg(f_line),5)) from r where run=%(run)s group by run,ps[1])
	,b as (select (p).sec as sec,(p).rev as rev,lower(unnest) as s,upper(unnest) as e from a)																											   
																													   
insert into routes(run,sec,reversed,s,e,note) 										  
select %(run)s,sec,rev,s,e,'auto' from b
	where not sec is null
	and 0=(select count(sec) from routes where routes.run=%(run)s and abs(routes.s-b.s)<5 and abs(routes.e-b.e)<5)--no existing entry with start and end within 50m
;

