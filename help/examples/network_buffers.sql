
--assume road is roundabout and geometry should be closed where startpoint within 1m of endpoint
update hsrr.network set geom = ST_AddPoint(geom, ST_StartPoint(geom)) WHERE 
st_dwithin(st_startPoint(geom),st_endPoint(geom),1) and not ST_IsClosed(geom);



--buffer around tightly curved linestring does strange things where it overlaps itself.
--fix by making around polygon.
update hsrr.network set buffer = case 
when st_isClosed(geom) then st_buffer(ST_MakePolygon(geom),30)
else st_buffer(geom,30)
end
