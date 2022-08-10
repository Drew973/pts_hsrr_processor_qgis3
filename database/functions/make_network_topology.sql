drop table if exists hsrr.n;
drop table if exists hsrr.n_noded;

create table hsrr.n as select id,geom as the_geom,null::int as source,null::int as target from hsrr.network where sec!='D';
select pgr_nodenetwork('hsrr.n',20.0);--doesn't seem to work with temp table.

select pgr_createTopology('hsrr.n_noded',20.0,clean := TRUE);


create table if not exists hsrr.n_noded
(id bigint)