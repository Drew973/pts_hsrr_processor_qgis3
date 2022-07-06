
--start and end chainages fuzzy. use pgrouting topology to node network and use those?
/*

CREATE OR REPLACE FUNCTION hsrr.recalc_edges(rn text)
RETURNS void AS $$

	delete from hsrr.edges;
	ALTER SEQUENCE hsrr.edges_pk_seq RESTART WITH 1;--reset sequence.

	insert into hsrr.edges(start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,cost)

	select start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch
	, hsrr.cost(run,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,run_geom)
	from hsrr.get_edges(rn);

	delete from hsrr.route_nodes;
	ALTER SEQUENCE hsrr.route_nodes_pk_seq RESTART WITH 1;

	insert into hsrr.route_nodes(run_ch)
	select distinct(start_run_ch) from hsrr.edges union
	select distinct(end_run_ch) from hsrr.edges;

	update hsrr.edges set source = route_nodes.pk from hsrr.route_nodes where start_run_ch = route_nodes.run_ch;
	update hsrr.edges set target = route_nodes.pk from hsrr.route_nodes where end_run_ch = route_nodes.run_ch;

	
	--join each node to all following nodes with dummy.
	--cost for multiple dummys slightly higher than 1 joining same nodes.
	--dummy cost =20*length + 1
	insert into hsrr.edges(start_run_ch,end_run_ch,source,target,sec,cost)
	select a.run_ch as start_run_ch,b.run_ch as end_run_ch, a.pk as source,b.pk as target,'D' as sec,20*(b.run_ch-a.run_ch)+1 as cost
	from
	hsrr.route_nodes as a inner join hsrr.route_nodes as b on a.run_ch<b.run_ch order by a.run_ch


$$ LANGUAGE sql;


select hsrr.recalc_edges('M62 SLIPS WB RE');
select * from hsrr.edges;



*/
---------------------------------------]





CREATE OR REPLACE FUNCTION hsrr.recalc_route_edges(rn text)
RETURNS void AS $$

	truncate hsrr.route_nodes RESTART IDENTITY;
	--empty table and reset sequences


	insert into hsrr.route_nodes(run_ch,pt)
	select s_ch+st_lineLocatePoint(vect,the_geom)*(e_ch-s_ch) as run_ch,the_geom
	from hsrr.noded_network_vertices_pgr inner join hsrr.readings on st_dwithin(the_geom,vect,15) and run = rn;

	--add gaps in run geometry,run start ,run end
	with a as (select s_ch,e_ch,vect,lead(vect) over (order by s_ch),lag(vect) over (order by s_ch) from hsrr.readings where run = rn)
	insert into hsrr.route_nodes(run_ch,pt)
	select e_ch,st_endPoint(vect) from a where lead is null or not st_dwithin(st_endPoint(vect),st_startPoint(lead),15)--gap after
	union
	select s_ch,st_startPoint(vect) from a where lag is null or not st_dwithin(st_endPoint(lag),st_startPoint(vect),15); --gap before


	truncate hsrr.route_edges RESTART IDENTITY;


	--dummys linking all sections
	insert into hsrr.route_edges(start_run_ch,end_run_ch,source,target)
	select s.run_ch,e.run_ch,s.pk,e.pk--hsrr.cost(rn text,start_run_ch numeric,end_run_ch numeric,sec_geom geometry)
	from hsrr.route_nodes as s inner join hsrr.route_nodes as e on s.run_ch<e.run_ch
	;

	--nearby sections with correct direction
	insert into hsrr.route_edges(start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,source,target,sec_geom)
	select start_run_ch
	,end_run_ch
	,sec
	,start_sec_ch
	,end_sec_ch
	,source
	,target
	,hsrr.network_geom(sec,start_sec_ch,end_sec_ch)

	from
	(
	select a.run_ch as start_run_ch,
	b.run_ch as end_run_ch
	,a.pk as source
	,b.pk as target
	,sec
	,has_forward
	,has_reverse
	,st_lineLocatePoint(geom,a.pt)*meas_len as start_sec_ch
	,st_lineLocatePoint(geom,b.pt)*meas_len as end_sec_ch
	from hsrr.route_nodes as a inner join hsrr.route_nodes as b on a.run_ch<b.run_ch
	inner join hsrr.network on st_dwithin(geom,a.pt,15) and st_dwithin(geom,b.pt,15)
	) a
	where (has_forward and start_sec_ch<end_sec_ch) or (has_reverse and start_sec_ch>end_sec_ch);

	update hsrr.route_edges set cost = hsrr.cost(rn,start_run_ch,end_run_ch,sec_geom)


$$ LANGUAGE sql;



--select hsrr.recalc_route_edges('A180 EB LE');
