CREATE OR REPLACE FUNCTION hsrr.routes_change() RETURNS TRIGGER AS $$
   BEGIN
      perform hsrr.process(new.sec,new.xsp);
      RETURN NEW;
   END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS routes_update on hsrr.routes;
CREATE TRIGGER routes_update after update
ON hsrr.routes
FOR EACH ROW EXECUTE PROCEDURE hsrr.routes_change();



CREATE OR REPLACE FUNCTION hsrr.routes_delete() RETURNS TRIGGER AS $$
   BEGIN
      perform hsrr.process(old.sec,old.xsp);
      RETURN NEW;
   END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS routes_delete on hsrr.routes;
CREATE TRIGGER routes_delete after delete
ON hsrr.routes
FOR EACH ROW EXECUTE PROCEDURE hsrr.routes_delete();