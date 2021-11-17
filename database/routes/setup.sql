
create schema if not exists routes;

set search_path to routes,public;


create table if not exists node
(
pk int primary key
,start_cost numeric--leave null
,previous_edge int--leave null
,visited bool
);


create table if not exists edge(
start_node int 
,end_node int
,cost numeric
,pk serial primary key
,unique(start_node,end_node)
);
create index on edge(start_node);
create index on edge(end_node);



CREATE OR REPLACE FUNCTION routes.visit_node(n int)
RETURNS void AS $$
	declare
		sc numeric = start_cost from node where pk=n;
	begin
		update node set start_cost = sc+cost,previous_edge=edge.pk from routes.edge where start_node=n and end_node=node.pk and (sc+cost<start_cost or start_cost is null);
		update node set visited=True where pk=n;
	end;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION array_reverse(a anyarray) RETURNS anyarray AS $$
SELECT array(select unnest from unnest(a) with ordinality order by ordinality desc)
$$ LANGUAGE sql IMMUTABLE;



/*
dijkstra's algorithm
finds cheapest path from node s to node e.
aborts after timeout nodes visited.
returns ordered array of edge ids
*/

--drop function 

CREATE OR REPLACE FUNCTION routes.cheapest_path(s int, e int,timeout int =10000)
RETURNS int[] AS $$

declare 
	current_node int = s;
	counter int = 0;
	r int[];
	current_edge int;
	
begin

	drop table if exists node;
	create temp table if not exists node--temp tables are unlogged
		(
		pk int primary key
		,start_cost numeric default null
		,previous_edge int default null
		,visited bool default false
		);


	insert into node(pk)
	select start_node from routes.edge 
	union --union gets distinct
	select end_node from routes.edge; 
	
	--update node set start_cost = null,visited=False;
	update node set start_cost=0,visited=True where node.pk=s;
	
	while counter<timeout and (not current_node is null) and not current_node=e loop
		perform routes.visit_node(current_node);
		current_node = (select node.pk from node where not visited and not start_cost is null order by start_cost limit 1);
		counter = counter+1;
	end loop;
		
	current_edge = (select previous_edge from node where pk=e);
	
	while not current_edge is null loop
		r = r||current_edge;
		current_edge = (select previous_edge from node where pk=(select start_node from routes.edge where pk=current_edge));
		--raise notice 'Current edge: %', current_edge;
	end loop;
	
	return routes.array_reverse(r);
	
end;

$$ LANGUAGE plpgsql;



/*
cheapest path connecting array of nodes in order.
*/

CREATE OR REPLACE FUNCTION routes.cheapest_path(nodes int[],timeout int =10000)
RETURNS int[] AS $$

begin
	return array(select unnest(routes.cheapest_path(unnest,lead,timeout)) from 
	(
	select unnest,lead(unnest) over(order by ordinality) from unnest(nodes) with ordinality
	) a
	where not lead is null);
		
end;
$$ LANGUAGE plpgsql;
