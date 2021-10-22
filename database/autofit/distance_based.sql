set search_path to hsrr,public;

delete from section_changes;

with a as (
	select sec,edge.geom,has_forward,has_reverse from network_topo.edge,network_topo.relation,network
WHERE edge.edge_id = relation.element_id
  AND relation.topogeo_id = (network.topo_geom).id
  )
    
,b as(
	select run,sec,False as reversed,st_distance(vect,st_startPoint(geom)),s_ch+st_linelocatePoint(vect,st_startPoint(geom))*(e_ch-s_ch) as ch,geom
	from a inner join readings on st_dwithin(geom,vect,200) and has_forward and vectors_align(geom,vect)
	
	union
	
	select run,sec,True as reversed,st_distance(vect,st_startPoint(geom)),s_ch+st_linelocatePoint(vect,st_endPoint(geom))*(e_ch-s_ch) as ch,geom
	from a inner join readings on st_dwithin(geom,vect,200) and has_reverse and vectors_align(geom,st_reverse(vect))
)

insert into section_changes(run,sec,reversed,ch)	
select run,sec,reversed,ch from b 
where (select count (ch) from b as c where c.sec=b.sec and c.reversed=b.reversed and abs(c.ch-b.ch)<200 and c.st_distance<b.st_distance )=0
order by run,ch,sec,reversed



set search_path to hsrr,public;

delete from section_changes;


with a as (select * from network_topo.edge_data inner join readings 
on st_dwithin(geom,vect,100))

,b as(
select run, False as reversed,sec,s_ch,e_ch,start_node,end_node,geom from a where vectors_align(vect,geom)
union 
select run,True,sec,s_ch,e_ch,start_node,end_node,geom from a where vectors_align(st_reverse(vect),geom)
)

--select run,sec,reversed,s_ch,e_ch from b 
--where (select count (ch) from b as c where c.sec=b.sec and c.reversed=b.reversed and abs(c.ch-b.ch)<200 and c.st_distance<b.st_distance )=0
--order by run,ch,sec,reversed

select * from b