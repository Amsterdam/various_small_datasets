-- DEMO data for dataset
-- Ice cream parlour dataset
-- Import this file in various_small_datasets database ,
-- and then you can try
--
-- http://localhost:8000/vsd/icp/1/
-- http://localhost:8000/vsd/icp/2/
-- http://localhost:8000/vsd/icp/3/

DROP TABLE IF EXISTS icp_data_new;
CREATE TABLE icp_data_new (
            icp_id integer NOT NULL PRIMARY KEY,
            naam character varying(128),
            prijs integer,
            sterren integer,
            smaken character varying(256),
            wkb_geometry geometry(Geometry,28992)
            );

ALTER TABLE icp_data_new ADD UNIQUE (naam);
CREATE INDEX ON icp_data_new USING gist(wkb_geometry);
INSERT INTO icp_data_new (icp_id, naam, prijs, sterren, smaken, wkb_geometry) VALUES
            (1, 'IJscuypje', 3, 4, 'pistache', ST_Transform(ST_GeomFromText('POINT(4.911880 52.367379)', 4326), 28992) ),
            (2, 'De ijsfiets', 2, 3, 'sinaasappel', ST_Transform(ST_GeomFromText('POINT(4.906130 52.365912)', 4326), 28992) ),
            (3, 'Het ijsboefje', 1, 4, 'straciatelli', ST_Transform(ST_GeomFromText('POINT(4.918146 52.358312)', 4326), 28992) );

ALTER TABLE IF EXISTS icp_data RENAME TO icp_data_old;
ALTER TABLE icp_data_new RENAME TO icp_data;
DROP TABLE IF EXISTS icp_data_old;

-- Here we update the catalog for the Ice Cream Parlour dataset

DELETE  FROM cat_dataset_fields where dataset_id = (select id from cat_dataset where name = 'icp');
DELETE  FROM cat_dataset where name = 'icp';

-- Import catalog
INSERT INTO cat_dataset(
	name,
    description,
    table_name,
    ordering,
    enable_api,
    name_field ,
    geometry_field,
    geometry_type,
    enable_geosearch,
    enable_maplayer
) VALUES(
    'icp', 'Ice Cream Parlours', 'icp_data', 'icp_id', true, 'naam', 'wkb_geometry', 'POINT', true, true);

WITH ins ("name", data_type, db_column, primary_key, "unique", max_length, blank, "null",
          max_digits, decimal_places, srid, dataset) AS
( VALUES
      ('id', 'integer', 'icp_id', true, false,  NULL, false, false, NULL::integer, NULL::integer, NULL, 'icp')
    , ('naam', 'char', NULL, false, true, 128, false, false, NULL, NULL, NULL, 'icp')
    , ('prijs', 'integer', NULL, false, false,  NULL, false, false, NULL, NULL, NULL, 'icp')
    , ('sterren', 'integer', NULL, false, false,  NULL, false, false, NULL, NULL, NULL, 'icp')
    , ('smaken', 'char', NULL, false, true, 128, false, false, NULL, NULL, NULL, 'icp')
    , ('locatie', 'geometry', 'wkb_geometry', false, false, NULL, false, false, NULL, NULL, 28992, 'icp')
)
INSERT INTO cat_dataset_fields(
	name,
    data_type,
    db_column,
    primary_key,
    "unique",
    max_length,
    blank,
    "null",
    max_digits,
    decimal_places,
    srid,
    dataset_id
)
SELECT ins.name, ins.data_type, ins.db_column, ins.primary_key, ins."unique", ins.max_length, ins.blank, ins."null",
       ins.max_digits, ins.decimal_places, ins.srid, cat_dataset.id
FROM cat_dataset JOIN ins on ins.dataset = cat_dataset.name;