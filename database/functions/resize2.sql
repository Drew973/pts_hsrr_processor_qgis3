delete from resized;



with a as (select sec,reversed,xsp,pk,unnest(to_ranges(meas_len(sec)::numeric,100)) as rg from requested)
	--insert into resized(sec,reversed,xsp,rg,s_ch,e_ch,geom)
	--select sec,reversed,xsp,rg,lower(rg) as s_ch,upper(rg) as e_ch,get_line(sec,lower(rg),upper(rg)) as geom from a
,b as 
	( 
	select
	a.sec
	,a.reversed
	,a.xsp
	,a.rg
	,array_agg(length(a.rg*fitted.rg) ORDER BY a.rg*fitted.rg DESC)::float[] as lengths
	,array_agg(rl ORDER BY a.rg*fitted.rg DESC) as vals
	,array_agg(fitted.pk ORDER BY a.rg*fitted.rg DESC) as pks
	from a left join fitted on a.sec=fitted.sec and a.reversed=fitted.reversed and a.xsp=fitted.xsp and a.rg&&fitted.rg
	group by a.sec,a.reversed,a.xsp,a.rg
	)


	insert into resized(sec,reversed,xsp,s_ch,e_ch,geom,pks,lengths,vals,rl)
	select sec,reversed,xsp
	,case when reversed then upper(rg) else lower(rg) end as s_ch
	,case when reversed then lower(rg) else upper(rg) end as e_ch
	,case when reversed then get_line(sec,upper(rg),lower(rg)) else get_line(sec,lower(rg),upper(rg)) end as geom
	,pks
	,lengths
	,vals
	,weighted_av(vals,lengths)
	from b
	