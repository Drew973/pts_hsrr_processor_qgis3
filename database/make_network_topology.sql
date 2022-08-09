drop table if exists n;
drop table if exists n_noded;

create table n as select id,geom as the_geom,null::int as source,null::int as target from hsrr.network where sec!='D';
select pgr_nodenetwork('n',20.0);--doesn't seem to work with temp table.

select pgr_createTopology('n_noded',20.0,clean := TRUE);