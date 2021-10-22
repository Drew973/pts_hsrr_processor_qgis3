set search_path to hsrr,public;


create table if not exists possible_changes
(ch float
,node_id int
,pt geometry
,pk int primary key);

--	-2 for gap after
--	-1 for gap before



--delete from possible_changes and recalculate for run rn
CREATE OR REPLACE FUNCTION calculate_possible_changes(rn text,min_chainage float=0.3,distance_tol float=100,gap_tol float=100)
RETURNS void AS $$
	delete from hsrr.possible_changes;
	
	with a as (select s_ch,e_ch,vect,lead(vect) over (order by s_ch),lag(vect) over(order by s_ch) from hsrr.readings where run = rn)
	
	,dists as (select s_ch+(e_ch-s_ch)*st_linelocatePoint(vect,geom) as ch,st_distance(vect,geom) as dist,node_id,geom as pt
	from network_topo.node inner join hsrr.readings on st_dwithin(vect,geom,distance_tol))

	insert into hsrr.possible_changes(pk,ch,node_id,pt)
	
	select row_number() over (order by ch,node_id),ch,node_id,pt from 
	(
	--passed nodes where no closer reading within min_chainage of chaiange
	select ch,node_id,pt from dists 
	where (select count(ch) from dists as dists2 where dists.node_id=dists2.node_id and dists2.dist<dists.dist and abs(dists.ch-dists2.ch)<min_chainage) =0
	group by ch,dist,node_id,pt
		
	union
		
	select e_ch,-2 as node_id,st_endPoint(vect) as pt from a where lead is null or not st_dwithin(vect,lead,gap_tol)--gap after
		
	union
		
	select s_ch,-1,st_startPoint(vect) from a where lag is null or not st_dwithin(vect,lag,gap_tol)--gap before
	) d
	
	;
$$ LANGUAGE sql;