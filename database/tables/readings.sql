set search_path to hsrr,public;

create table if not exists readings
(
pk serial primary key
,run text references run_info(run) on update cascade
,f_line int--which line of file data came from
,t timestamptz
,raw_ch numeric--machine chainage from file. start or end?
,rl numeric--reading
,vect geometry('Linestring',27700)
,s_ch numeric--chainage of start in km
,e_ch numeric--chainage of end in km
,rg numrange
);

create index on readings using gist(vect);
create index on readings(run);
