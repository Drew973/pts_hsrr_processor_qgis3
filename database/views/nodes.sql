create view nodes as
select ST_Centroid(unnest(ST_ClusterWithin(g,20))) as p from
(select st_startPoint(geom) as g from network 
union select st_endPoint(geom) from network)ends;