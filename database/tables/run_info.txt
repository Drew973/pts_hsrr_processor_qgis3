
create table if not exists hsrr.run_info(
run varchar primary key,
file varchar unique --don't allow more than 1 run/file
)

