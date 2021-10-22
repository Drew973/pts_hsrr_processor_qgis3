set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION autofit(rn text)
RETURNS table (pk int) AS $$

	with a as(
		select ch,pt from gaps where run=rn
		union
		select ch,pt from passed_nodes where run=rn
	)
	,b as (select ch,array_agg(pt) from a group by ch)
	,c as (select 'A69 DBFO EB CL1',ch,array_agg[1] as pt,'auto' from b where not ch in (select ch from section_changes where run='A69 DBFO EB CL1'))
	,d as (select ch,pt,best_sr(st_makeLine(pt,lead(pt) over (order by ch))) from c)
	
	insert into section_changes(run,ch,pt,note,sec,reversed)
	select rn,ch,pt,'auto',(best_sr).sec,(best_sr).rev from d
	returning pk;



$$ LANGUAGE sql;



CREATE OR REPLACE FUNCTION autofit(rn text)
RETURNS table (pk int) AS $$

	insert into hsrr.section_changes(run,ch,pt,note,sec,reversed)
	select rn,ch,st_startPoint(geom),'auto',sec,reversed from hsrr.possible_sections where run=rn
	returning pk;



$$ LANGUAGE sql;


alter function autofit set search_path to hsrr,public;

--with a as (select pk,best_sr(st_MakeLine(pt,lead(pt) over(order by ch))) from section_changes where run='SEW NB CL1')
	--update section_changes set sec = (best_sr).sec, reversed = (best_sr).rev from a where a.pk=section_changes.pk and note='auto'