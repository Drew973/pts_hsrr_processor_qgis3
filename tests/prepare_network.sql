insert into hsrr.network(sec,geom,meas_len,has_forward,has_reverse,funct) 
select sec,geom,meas_len,has_forward,has_reverse,funct from nwk where sec!='D'



/*
network geometry should be closed for roundabouts. Often won't be in client networks.
assume roundabout and close geometry where startPoint within 1m of endPoint.
*/
update hsrr.network set geom = ST_AddPoint(geom, ST_StartPoint(geom)) WHERE 
st_dwithin(st_startPoint(geom),st_endPoint(geom),1) and not ST_IsClosed(geom);


/*
buffer is used for autofitting.

For best results buffer should extend past ends of section
30m is about right size.

buffer around linestring will do strange things where it overlaps itself.
problem for small roundabouts
buffer around polygon rather than linestring for closed geom
*/
update hsrr.network set buffer = case 
when st_isClosed(geom) then st_buffer(ST_MakePolygon(geom),30)
else st_buffer(geom,30)
end