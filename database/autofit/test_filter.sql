drop table if exists test_filter;

create table test_filter as

select run,sec,start_sec_ch,end_sec_ch,start_run_ch,end_run_ch,run_geom,
(
	select count(sec)=1 from hsrr.section_changes 
 	where run='M62 SLIPS WB RE' and section_changes.sec=get_edges.sec 
	and abs(section_changes.start_sec_ch-get_edges.start_sec_ch)<0.1
	and abs(section_changes.end_sec_ch-get_edges.end_sec_ch)<0.1
	and abs(section_changes.ch-get_edges.start_run_ch)<0.1
	and abs(section_changes.e_ch-get_edges.end_run_ch)<0.1
) as correct
,hsrr.cost(run,start_run_ch,end_run_ch,sec,start_sec_ch,end_sec_ch,run_geom) as cost 


from hsrr.get_edges('M62 SLIPS WB RE');
--hsrr.cost(run text,start_run_ch numeric,end_run_ch numeric,sec text,start_sec_ch numeric,end_sec_ch numeric,run_geom geometry)


select sec,cost,correct,start_run_ch,end_run_ch from test_filter

