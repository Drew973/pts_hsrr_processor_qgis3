set search_path to hsrr,public;


create table if not exists network
    (
    sec text primary key
	,geom geometry('linestring',27700)
	,meas_len float
	--,buff geometry('polygon',27700)
	,has_forward bool
	,has_reverse bool
    );
