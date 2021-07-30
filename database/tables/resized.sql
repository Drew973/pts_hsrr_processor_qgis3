create table if not exists hsrr.resized(
sec varchar,
reversed bool,
xsp varchar,
s_ch int,
e_ch int,
pks int[],
vals int[],
lengths int[],
RL int,
geom geometry('linestring',27700)
);

--create index if not exists rg_ind on hsrr.resized using gist(rg);
create index if not exists sec_ind on hsrr.resized(sec);
create index if not exists xsp_ind on hsrr.resized(xsp);
create index if not exists rev_ind on hsrr.resized(reversed);

