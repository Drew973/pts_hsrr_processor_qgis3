drop table if exists run_geoms;


create table if not exists run_geoms as
select run,ST_LineMerge(ST_union(vect order by s_ch asc,50)) as run_geom
from hsrr.readings inner join hsrr.network on st_dwithin(vect,geom,50) group by run;
