
--insert rows into resized from requested table


delete from hsrr.resized;

with a as 
	(
	select network.sec,reversed,xsp,geom,meas_len::numeric
	from hsrr.requested inner join hsrr.network 
	on network.sec=requested.sec
	)

,b as
	(
	select sec,reversed,xsp,meas_len,geom,generate_series(0,meas_len,0.1) as start_chain from a
	)
	
,c as 
	(
	select sec,reversed,xsp,meas_len,geom,start_chain,least(start_chain+0.1,meas_len) as end_chain from b
	)
	
	insert into hsrr.resized(sec,reversed,xsp,s_ch,e_ch,geom,rg)
	select 
		sec
		,reversed
		,xsp
		,start_chain
		,end_chain
		,ST_LineSubstring(geom,(start_chain/meas_len)::float,(end_chain/meas_len)::float)
		,numrange(least(start_chain,end_chain),greatest(start_chain,end_chain))
	from c where start_chain!=end_chain;


--select * from hsrr.resized;