drop table if exists hsrr.staging;

create table hsrr.staging(
raw_ch float,
ts varchar,
rl float,
start_lon float,
start_lat float,
end_lon float,
end_lat float,
f_line int,
run varchar,
start_point geometry('point',27700),
end_point geometry('point',27700)
)