
CREATE OR REPLACE FUNCTION hsrr.refit() 
	RETURNS void AS $$

	--refit everything
	--5-10s for all area 12.
	delete from hsrr.fitted;

	with a as
	(
	select 
	r.run,sec,(c.start_sec_ch>c.end_sec_ch) as reversed,c.xsp,vect,rl

	,greatest(hsrr.interpolate_2d(r.s_ch,c.ch,start_sec_ch,c.e_ch,end_sec_ch),0) as s
	,least(hsrr.interpolate_2d(r.e_ch,c.ch,start_sec_ch,c.e_ch,end_sec_ch),hsrr.meas_len(sec)::numeric) as e

	from hsrr.section_changes as c inner join hsrr.readings as r on
	hsrr.to_numrange(r.s_ch,r.e_ch,'[]')&&hsrr.to_numrange(c.ch,c.e_ch)
	and r.run = c.run
	and not sec='D'
	)

	insert into hsrr.fitted(run,sec,reversed,xsp,vect,rl,s_ch,e_ch,rg)
	select run,sec,reversed,xsp,vect,rl,s,e,numrange(least(s,e),greatest(s,e)) from a
	$$ language sql;

--select hsrr.refit();
