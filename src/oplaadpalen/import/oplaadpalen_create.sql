BEGIN;
DROP TABLE IF EXISTS oplaadpalen_new;

CREATE TABLE oplaadpalen_new
(
  id                  SERIAL PRIMARY KEY,
  cs_external_id      character varying(32) NOT NULL,
  wkb_geometry        geometry(Geometry,28992),
  street              character varying(150),
  housenumber         character varying(6),
  housnumberext       character varying(6),
  postalcode          character varying(6),
  district            character varying(40),
  countryiso          character varying(3),
  region              character varying(40),
  city                character varying(40),
  provider            character varying(40),
  restrictionsremark  character varying(128),
  charging_point      integer,
  -- The following items are  per charging point.
  -- If they are the same we show only one value otherwise we store a list separated with ;
  status              character varying(32),
  connector_type      character varying(32),
  vehicle_type        character varying(32),
  charging_capability character varying(32),
  identification_type character varying(32)
);

ALTER TABLE oplaadpalen_new ADD CONSTRAINT cs_external_id_unique_new UNIQUE (cs_external_id);
CREATE INDEX oplaadpalen_new_wkb_geometry_geom_idx ON oplaadpalen_new USING gist (wkb_geometry);
COMMIT;