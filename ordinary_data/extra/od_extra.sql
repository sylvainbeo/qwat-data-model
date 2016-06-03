/*
    qWat - QGIS Water Module

    SQL file :: extra tables (test)
*/


CREATE TABLE qwat_od.extra ();
COMMENT ON TABLE qwat_od.extra IS 'Test table';

/* COLUMNS */
ALTER TABLE qwat_od.extra ADD COLUMN id SERIAL PRIMARY KEY;