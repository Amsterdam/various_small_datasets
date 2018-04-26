BEGIN;

DROP TABLE IF EXISTS iot_locations_new;
DROP TABLE IF EXISTS iot_owners_new;
DROP TABLE IF EXISTS iot_things_new;

CREATE TABLE iot_things_new (
    id varchar(64) PRIMARY KEY NOT NULL,
    ref character varying(128),
    name character varying(128),
    description text,
    device_type varchar(32),
    purpose text
);

CREATE TABLE iot_locations_new (
    id SERIAL PRIMARY KEY,
    thing_id varchar(64) REFERENCES iot_things_new(id),
    ref varchar(128),
    name varchar(128),
    rd_geometry geometry(Geometry,28992),
    wgs84_geometry geometry(Geometry,4326)
);

CREATE TABLE iot_owners_new (
    id UUID PRIMARY KEY,
    thing_id varchar(64) REFERENCES iot_things_new(id),
    name varchar(128),
    email varchar(128)
);

COMMIT;
