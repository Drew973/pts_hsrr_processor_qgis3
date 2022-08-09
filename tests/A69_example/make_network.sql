delete from hsrr.routes;
delete from hsrr.requested;
delete from hsrr.network;


insert into hsrr.network(sec,geom,meas_len,id,has_forward,has_reverse)
select sec,geom,meas_len,id,has_forward,has_reverse from a69_network;
