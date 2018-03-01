CREATE TABLE biz_data (
    biz_id integer PRIMARY KEY NOT NULL,
    naam character varying(128),
    biz_type character varying(64),
    heffingsgrondslag  character varying(128),
    website  character varying(128),
    heffing numeric(10, 2),
    bijdrageplichtigen integer,
    verordening  character varying(128),
    wkb_geometry  geometry(Geometry,28992)
);

ALTER TABLE biz_data ADD CONSTRAINT naam_unique UNIQUE (naam);
CREATE INDEX biz_data_wkb_geometry_geom_idx ON biz_data USING gist (wkb_geometry);

