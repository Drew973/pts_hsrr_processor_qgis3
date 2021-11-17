set search_path to hsrr,public;

--select * from resized_view;


CREATE OR REPLACE FUNCTION process(sect text,rev bool,lane text,piece_length numeric =100) 
RETURNS void AS $$
		Declare
			meas_len numeric=meas_len from network where sec=sect;
        BEGIN	
			--fitted
			delete from hsrr.fitted where sec=sect and reversed=rev and xsp=lane;
			
			with a as (select run,ch
			,(select min(ch) from section_changes where run=sc.run and ch>sc.ch) as next_ch
			from section_changes as sc where sec=sect and reversed=rev and xsp=lane--100ms; -- IS NOT DISTINCT FROM
			)
			, b as (select vect,rl,readings.pk
				,meas_sec_ch(sect,st_startPoint(vect))::numeric as s_ch
				,meas_sec_ch(sect,st_endPoint(vect))::numeric as e_ch
				from a inner join readings on a.run=readings.run and numrange(ch,next_ch)&&numrange(s_ch,e_ch)
				)
				insert into hsrr.fitted(sec,reversed,xsp,vect,rl,s_ch,e_ch,readings_pk,rg)
				select sect,rev,lane,vect,rl,s_ch,e_ch,pk,numrange(least(s_ch,e_ch),greatest(s_ch,e_ch)) from b;

			--resized
			delete from hsrr.resized where sec=sect and reversed=rev and xsp=lane;
			
			with a as (select unnest(to_ranges(meas_len(sect)::numeric,piece_length)) as r)
			, b as (select r,(rl,upper(r*rg)-lower(r*rg))::weighted_val as v from fitted inner join a on fitted.rg&&r and fitted.sec=sect and fitted.reversed=rev and fitted.xsp=lane)
			
			insert into resized(sec,reversed,xsp,s_ch,e_ch,vals,rl,geom)
			
			select sect,rev,lane
			,case when rev then upper(r) else lower(r) end as s_ch
			,case when rev then lower(r) else upper(r) end as e_ch
			,array_agg(v)::text as vals
			,weighted_av(array_agg(v)) as rl
			,case when rev then get_line(sect,upper(r),lower(r)) else get_line(sect,lower(r),upper(r)) end as geom
			from b group by r;

		END		
$$
set search_path to hsrr,public
LANGUAGE plpgsql;