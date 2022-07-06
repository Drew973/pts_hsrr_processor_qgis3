

--update resized from fitted.
--very efficient, 3s for all of area 12



with a as
(
select resized.pk 
,array_agg((fitted.rl,upper(fitted.rg*resized.rg)-lower(fitted.rg*resized.rg))::hsrr.weighted_val) as vals
from hsrr.resized inner join hsrr.fitted

on fitted.sec=resized.sec 
and fitted.xsp=resized.xsp 
and fitted.reversed=resized.reversed 
and fitted.rg&&resized.rg

group by resized.pk
)

update hsrr.resized set vals=a.vals::text,rl=hsrr.weighted_av(a.vals) 
from a where a.pk=resized.pk




CREATE OR REPLACE FUNCTION hsrr.update_resized() 
	RETURNS void AS $$

	with a as
	(
	select resized.pk 
	,array_agg((fitted.rl,upper(fitted.rg*resized.rg)-lower(fitted.rg*resized.rg))::hsrr.weighted_val) as vals
	from hsrr.resized inner join hsrr.fitted

	on fitted.sec=resized.sec 
	and fitted.xsp=resized.xsp 
	and fitted.reversed=resized.reversed 
	and fitted.rg&&resized.rg

	group by resized.pk
	)

	update hsrr.resized set vals=a.vals::text,rl=hsrr.weighted_av(a.vals) 
	from a where a.pk=resized.pk;
	
	$$ language sql