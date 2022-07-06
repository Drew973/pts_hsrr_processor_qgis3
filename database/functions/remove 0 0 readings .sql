--delete where vect within 10m of 0,0 of ESPG 4326
delete from hsrr.readings where st_dwithin(vect,St_Transform(ST_SetSRID(st_makePoint(0,0),4326),27700),10)

