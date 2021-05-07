set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION routes_iu()
  RETURNS trigger AS
$$
BEGIN
	perform process(new.sec,new.reversed,new.xsp);
    RETURN new;
END;
$$
LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION routes_d()
  RETURNS trigger AS
$$
BEGIN
	perform process(old.sec,old.reversed,old.xsp);
    RETURN new;
END;
$$
LANGUAGE 'plpgsql';


drop trigger if exists routes_iu on routes;
create trigger routes_iu after insert or update on routes
for each row
EXECUTE PROCEDURE routes_iu();


drop trigger if exists routes_d on routes;
create trigger routes_d after delete on routes
for each row
EXECUTE PROCEDURE routes_d();