drop view if exists passed_nodes;

create view passed_nodes as

select *,row_number() over (order by f_line) from
(
select run,f_line+st_lineLocatePoint(vect,p) as f_line,st_closestPoint(vect,p) as p from readings inner join nodes on st_dwithin(vect,p,10)
union
select run,f_line,p from discontinuities
)a;