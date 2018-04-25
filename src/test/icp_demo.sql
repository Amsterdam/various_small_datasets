-- DEMO data for dataset
-- Ice cream parlour dataset
-- Import this file in various_small_datasets database ,
-- and then you can try
--
-- http://localhost:8000/vsd/ijs/1/
-- http://localhost:8000/vsd/ijs/2/
-- http://localhost:8000/vsd/ijs/3/

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

DELETE  FROM cat_dataset_fields where dataset_id = (select id from cat_dataset where name = 'ijs');
DELETE  FROM cat_dataset where name = 'ijs';

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
    'ijs', 'IJs Salons rond de Weesperstraat', 'icp_data', 'id', true, 'naam', 'wkb_geometry', 'POINT', true, true);
