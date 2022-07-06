CREATE OR REPLACE FUNCTION hsrr.sec_changes_iu()
  RETURNS trigger AS
$$
BEGIN
	perform hsrr.process(new.sec,new.reversed,new.xsp);
    RETURN new;
END;
$$
LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION hsrr.sec_changes_del()
  RETURNS trigger AS
$$
BEGIN
	perform hsrr.process(old.sec,old.reversed,old.xsp);
    RETURN old;
END;
$$
LANGUAGE 'plpgsql';


drop trigger if exists sec_changes_iu on hsrr.section_changes;
create trigger sec_changes_iu after insert or update on hsrr.section_changes
for each row
EXECUTE PROCEDURE hsrr.sec_changes_iu();


drop trigger if exists sec_changes_del on hsrr.section_changes;
create trigger sec_changes_del after delete on hsrr.section_changes
for each row
EXECUTE PROCEDURE hsrr.sec_changes_del();