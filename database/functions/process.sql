
CREATE OR REPLACE FUNCTION hsrr.process() 
RETURNS void AS $$
	select hsrr.refit();
	select hsrr.update_resized();
	select hsrr.recalc_coverage();
	$$
LANGUAGE sql;




CREATE OR REPLACE FUNCTION hsrr.process(sect text,xs text) 
RETURNS void AS $$
	select hsrr.refit(sect,xs);
	select hsrr.update_resized(sect,xs);
	select hsrr.recalc_coverage(sect,xs,True);
	select hsrr.recalc_coverage(sect,xs,False);
	$$
LANGUAGE sql;