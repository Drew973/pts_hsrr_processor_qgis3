

drop type if exists sec_rev cascade;

-- no if exists for type

CREATE TYPE sec_rev AS
   (
     sec VARCHAR,
     rev bool
   );