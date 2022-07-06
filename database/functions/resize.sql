

set search_path to hsrr,public;


with a as (select sec,reversed,xsp,get_pieces(sec) from requested)
,pieces as (select sec,reversed,xsp,(get_pieces).s_ch,(get_pieces).e_ch,(get_pieces).geom,(get_pieces).rg from a)


,b as (
select pieces.sec
	,pieces.reversed
	,pieces.xsp
	,s_ch
	,e_ch
	,array_agg(fitted.pk order by fitted.rg*pieces.rg) as pks
	,array_agg(fitted.rl order by fitted.rg*pieces.rg),array_agg(fitted.rl order by fitted.rg*pieces.rg) as vals	
	,array_agg(upper(fitted.rg*pieces.rg)-lower(fitted.rg*pieces.rg) order by fitted.rg*pieces.rg )::float[] as lengths
	,geom

from pieces left join fitted on pieces.sec=fitted.sec and pieces.reversed=fitted.reversed and pieces.xsp=fitted.xsp and pieces.rg&&fitted.rg
group by pieces.sec,pieces.reversed,pieces.xsp,s_ch,e_ch,geom
)

insert into resized(sec,reversed,xsp,s_ch,e_ch,geom,pks,vals,lengths,rl)
select sec,reversed,xsp,s_ch,e_ch,geom,pks,vals,lengths,weighted_av(vals,lengths) from b



/*
--not dependent on requested table.
--means unrequested sections can be in results. probably not big deal and easy to remove if so with

delete from hsrr.resized
where (select count(sec) from hsrr.requested where requested.sec=resized.sec and requested.xsp=resized.xsp and requested.reversed=resized.reversed)
=0


--not needing to make requested table good as often don't know what section/direction,xsps requested.

*/
CREATE OR REPLACE FUNCTION hsrr.resize(sect varchar,rev bool,xs varchar)
	RETURNS void AS $$
	
	BEGIN
	
	delete from hsrr.resized where sec=sect and rev = reversed and xsp=xs;
	
	with a as(
	select s,e,g
	,(rl,upper(r*rg)-lower(r*rg))::hsrr.weighted_val as val
	from hsrr.get_pieces(sect) left join hsrr.fitted
	on sec = sect and xsp=xs and reversed = rev and rg&&r
	)
	insert into hsrr.resized(sec,reversed,xsp,s_ch,e_ch,vals,rl,geom)
	select sect,rev,xs,s,e
	,array_agg(val)::text
	,hsrr.weighted_av(array_agg(val))
	,g
	from a
	group by s,e,g;
	
	END;
$$ LANGUAGE plpgsql;



--select hsrr.resize(sec,reversed,xsp) from hsrr.requested;
--30s
