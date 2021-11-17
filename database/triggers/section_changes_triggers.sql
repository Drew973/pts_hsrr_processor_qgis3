set search_path to hsrr,public;


CREATE OR REPLACE FUNCTION sec_changes_iu()
  RETURNS trigger AS
$$
BEGIN
	perform hsrr.process(new.sec,new.reversed,new.xsp);
    RETURN new;
END;
$$
set search_path to hsrr,public
LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION before_sec_changes_iu()
  RETURNS trigger AS
$$
BEGIN
	new.pt = hsrr.run_ch_to_pt(new.run,new.ch);
    RETURN new;
END;
$$
set search_path to hsrr,public
LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION sec_changes_del()
  RETURNS trigger AS
$$
BEGIN
	perform hsrr.process(old.sec,old.reversed,old.xsp);
    RETURN new;
END;
$$
set search_path to hsrr,public
LANGUAGE 'plpgsql';


drop trigger if exists sec_changes_iu on section_changes;
create trigger sec_changes_iu after insert or update on section_changes
for each row
EXECUTE PROCEDURE sec_changes_iu();


drop trigger if exists sec_changes_geom on section_changes;
create trigger sec_changes_geom before insert or update on section_changes
for each row
EXECUTE PROCEDURE before_sec_changes_iu();


drop trigger if exists sec_changes_del on section_changes;
create trigger sec_changes_del after delete on section_changes
for each row
EXECUTE PROCEDURE sec_changes_del();