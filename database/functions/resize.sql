CREATE OR REPLACE FUNCTION hsrr.resize() 
	RETURNS void AS $$
	
	BEGIN
	
	delete from hsrr.resized;
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
	,array_agg(upper(a.rg*fitted.rg)-lower(a.rg*fitted.rg) ORDER BY a.rg*fitted.rg DESC)::float[] as lengths
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
	from b;
																				   
	perform hsrr.recalc_coverage();																																			  
	END;			
$$ LANGUAGE plpgsql;


alter function hsrr.resize() set search_path=hsrr,public;


CREATE OR REPLACE FUNCTION hsrr.resize(rn varchar) 
	RETURNS void AS $$
	Declare
		sects varchar[]=array(select distinct sec from hsrr.routes where run=rn);--sections in run		

	BEGIN
	
	delete from hsrr.resized where sec=any(sects);

	insert into hsrr.resized (sec,reversed,xsp,s_ch,e_ch,lengths,pks,vals)
	select p.sec,p.reversed,p.xsp,p.s_ch,p.e_ch,array_agg(upper(p.rg*fitted.rg)-lower(p.rg*fitted.rg)) as lengths,array_agg(pk) as pks,array_agg(rl) as vals from (select sec,reversed,xsp,(gp).s_ch,(gp).e_ch,int4range(least((gp).s_ch,(gp).e_ch)::int,greatest((gp).s_ch,(gp).e_ch)::int) as rg from (select sec,reversed,xsp,get_pieces(sec) as gp from requested)a)p
	left join fitted on p.sec=fitted.sec and p.reversed=fitted.reversed and p.xsp=fitted.xsp and p.rg&&fitted.rg and p.sec=any(sects)
	group by p.sec,p.reversed,p.xsp,p.s_ch,p.e_ch;


	update hsrr.resized set 
	rl=weighted_av(vals,lengths),
	geom=case when reversed then get_line(sec,e_ch,cast(s_ch as float)) when not reversed then get_line(sec,cast(s_ch as float),e_ch) end 
	where sec=any(sects);

	perform hsrr.recalc_coverage();																																			  
	END;			
$$ LANGUAGE plpgsql;
--2s


alter function hsrr.resize(rn varchar) set search_path=hsrr,public;



CREATE OR REPLACE FUNCTION hsrr.resize(sect varchar,rev bool,xs varchar) 
	RETURNS void AS $$
	BEGIN
	
	delete from hsrr.resized where sec=sect and reversed=rev and xsp=xs;

	if (select count(sec)>0 from requested where sec=sect and reversed=rev and xsp=xs) then--in requested
		
		insert into hsrr.resized (sec,reversed,xsp,s_ch,e_ch,pks,vals,lengths,rl,geom)
		select sect,rev,xs,s_ch,e_ch
		,array(select pk from fitted where sec=sect and reversed=rev and xsp=xs and fitted.rg&&a.rg)
		,array(select rl from fitted where sec=sect and reversed=rev and xsp=xs and fitted.rg&&a.rg)
		,array(select upper(fitted.rg*a.rg)-lower(fitted.rg*a.rg) from fitted where sec=sect and reversed=rev and xsp=xs and fitted.rg&&a.rg)
		,weighted_av(array(select rl::int from fitted where sec=sect and reversed=rev and xsp=xs and fitted.rg&&a.rg),array(select upper(fitted.rg*a.rg)-lower(fitted.rg*a.rg) from fitted where sec=sect and reversed=rev and xsp=xs and fitted.rg&&a.rg))
		,get_line(sect,least(s_ch,e_ch),greatest(s_ch,e_ch))
		from (select (get_pieces).s_ch,(get_pieces).e_ch,int4range((get_pieces).s_ch::int,(get_pieces).e_ch::int,'[]')as rg from get_pieces(sect))a;

	end if;
	END;			
$$ LANGUAGE plpgsql;


alter function hsrr.resize(sect varchar,rev bool,xs varchar) set search_path=hsrr,public;








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










