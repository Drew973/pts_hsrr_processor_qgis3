with a as 
(
	select pk,
COALESCE (lead(ch) over (partition by run order by ch),(select max(e_ch) from hsrr.readings where run=c.run)) as e

from hsrr.section_changes as c

)

update hsrr.section_changes set e_ch = e from a 
where a.pk = hsrr.section_changes.pk and not ch<e_ch;