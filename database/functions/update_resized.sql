

--update resized from fitted.
--very efficient, 3s for all of area 12
CREATE OR REPLACE FUNCTION hsrr.update_resized() 
	RETURNS void AS $$

	with a as
	(
	select resized.pk 
	,array_agg((fitted.rl,hsrr.length(hsrr.to_numrange(resized.s_ch,resized.e_ch,'()')*fitted.rg))::hsrr.weighted_val) as vals
	from hsrr.resized inner join hsrr.fitted

	on fitted.sec=resized.sec 
	and fitted.xsp=resized.xsp 
	and fitted.reversed=resized.reversed 
	and fitted.rg&&hsrr.to_numrange(resized.s_ch,resized.e_ch,'()')

	group by resized.pk
	)

	update hsrr.resized set vals=a.vals::text,rl=hsrr.weighted_av(a.vals) 
	from a where a.pk=resized.pk;
	
	$$ language sql;
	
	
	
/*
update resized from fitted for section and xsp.
*/
CREATE OR REPLACE FUNCTION hsrr.update_resized(sect text,xp text) 
	RETURNS void AS $$

	with a as
	(
	select resized.pk 
	,array_agg((fitted.rl,hsrr.length(hsrr.to_numrange(resized.s_ch,resized.e_ch,'()')*fitted.rg))::hsrr.weighted_val) as vals
	from hsrr.resized inner join hsrr.fitted

	on fitted.sec = sect
	and resized.sec = sect
	and fitted.xsp = xp
	and resized.xsp = xp
	and fitted.reversed=resized.reversed 
	and fitted.rg&&hsrr.to_numrange(resized.s_ch,resized.e_ch,'()')

	group by resized.pk
	)

	update hsrr.resized set vals=a.vals::text,rl=hsrr.weighted_av(a.vals) 
	from a where a.pk=resized.pk;
	
	$$ language sql