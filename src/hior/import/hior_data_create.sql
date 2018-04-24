BEGIN;

DROP TABLE IF EXISTS hior_attributes_new;
DROP TABLE IF EXISTS hior_properties_new;
DROP TABLE IF EXISTS hior_items_new;

CREATE TABLE hior_items_new (
    id integer PRIMARY KEY NOT NULL,
    text text,
    description text
);

CREATE TABLE hior_attributes_new (
    id SERIAL PRIMARY KEY,
    item_id integer REFERENCES hior_items_new(id),
    name character varying(128),
    value character varying(512)
);

CREATE TABLE hior_properties_new (
    id SERIAL PRIMARY KEY,
    item_id integer REFERENCES hior_items_new(id),
    name character varying(128),
    value character varying(128)
);

COMMIT;
