
create table if not exists hsrr.readings
(
pk serial primary key
,run text references hsrr.run_info(run) on update cascade on delete cascade
,f_line int--which line of file data came from
,t timestamptz
,raw_ch numeric--machine chainage from file. start or end?
,rl numeric--reading
,vect geometry('Linestring',27700)
,s_ch numeric--chainage of start in km
,e_ch numeric--chainage of end in km
);

create index on hsrr.readings using gist(vect);
create index on hsrr.readings(run);
create index on hsrr.readings(hsrr.to_numrange(s_ch,e_ch,'[]'));
