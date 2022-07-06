
--alter table hsrr.network add column id serial;
--ALTER TABLE hsrr.network ADD id int8 NOT NULL GENERATED ALWAYS AS IDENTITY;


--make into function?
--or just leave in help?


create table hsrr.noded_network as select id,geom as the_geom,null::int as source,null::int as target from hsrr.network;

select pgr_createTopology('hsrr.noded_network',5)

--select *,st_asText(the_geom) from hsrr.noded_network_vertices_pgr