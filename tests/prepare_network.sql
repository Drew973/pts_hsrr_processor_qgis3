insert into hsrr.network(sec,geom,meas_len,has_forward,has_reverse,funct) 
select sec,geom,meas_len,has_forward,has_reverse,funct from nwk where sec!='D'
