CREATE OR REPLACE FUNCTION process_sec(sect varchar,rev bool,xp varchar) 
RETURNS void as $$		
	DECLARE
		geom geometry=geom from network where sec=sect;
		ml float =meas_len from network where sec=sect;

        BEGIN
			--redo fitted for sec,rev,xsp
			delete from fitted where sec=sect and reversed=rev and xsp=xp;
			
			insert into fitted(sec,reversed,xsp,run,f_line,vect,s_ch,e_ch,rl,rq) select
			sec
			,reversed
			,xsp
			,routes.run
			,f_line
			,vect
			,meas_sec_ch(sec,s_point)
			,meas_sec_ch(sec,e_point)
			,rl
			,case when s_ch<=e_ch then int4range (s_ch::int,e_ch::int) else int4range (e_ch::int,s_ch::int) end as rq
			from routes inner join readings on readings.run=rn and routes.s_line<=readings.f_line and readings.f_line<=routes.e_line and routes.run=rn;

			--redo resized
			delete from resized where sec=sect and reversed=rev and xsp=xp;
			insert into resized(sec,reversed,xsp,s_ch,e_ch,pks,vals,lengths,geom,rl)
			
			select sec,reversed,xsp,s_ch,e_ch,pks,vals,lengths,case when reversed then get_line(sec,e_ch,cast(s_ch as float)) when not reversed then get_line(sec,cast(s_ch as float),e_ch) end ,weighted_av(lengths,vals::int[])
				from
					(select p.sec as sec
					,p.reversed as reversed
					,p.xsp as xsp
					,p.s_ch as s_ch
					,p.e_ch
					,array_agg(pk) as pks
					,array_agg(rl order by upper(r*rg)-lower(r*rg)) as vals
					,array_agg(upper(r*rg)-lower(r*rg) order by upper(r*rg)-lower(r*rg)) as lengths 
					--,case when p.reversed then get_line(p.sec,p.e_ch,cast(p.s_ch as float)) when not p.reversed then get_line(p.sec,cast(p.s_ch as float),p.e_ch) end																												   

					from 
					(select sect as sec,rev as reversed,xp as xsp,s_ch,e_ch,int4range(s_ch::int,e_ch::int) as r from get_pieces(sect)) p
					left join fitted on fitted.sec=p.sec and fitted.xsp=p.xsp and fitted.reversed=p.reversed and r&&rg
					group by p.sec,p.reversed,p.xsp,p.s_ch,p.e_ch
					)a;		
	 
	--update resized set rl=weighted_av(lengths,vals) where sec=sect and xsp=xsp and reversed=rev;
		
			
		END;
$$ LANGUAGE plpgsql;