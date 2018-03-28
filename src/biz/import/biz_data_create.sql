DROP VIEW IF EXISTS biz_view;
DROP TABLE IF EXISTS biz_data;

CREATE TABLE biz_data (
    biz_id integer PRIMARY KEY NOT NULL,
    naam character varying(128),
    biz_type character varying(64),
    heffingsgrondslag  character varying(128),
    website  character varying(128),
    heffing integer,
    bijdrageplichtigen integer,
    verordening  character varying(128),
    wkb_geometry  geometry(Geometry,28992)
);

ALTER TABLE biz_data ADD CONSTRAINT naam_unique UNIQUE (naam);
CREATE INDEX biz_data_wkb_geometry_geom_idx ON biz_data USING gist (wkb_geometry);

CREATE VIEW biz_view AS SELECT
    biz_id,
    naam,
    biz_type,
    heffingsgrondslag ,
    website,
    heffing,
    'EUR' as heffing_valuta_code,
    CASE heffing IS NULL
    WHEN True THEN
        NULL
    ELSE
        concat(E'\u20AC', ' ', cast(heffing as character varying(10)))
    END as heffing_display,
    bijdrageplichtigen,
    verordening ,
    wkb_geometry
FROM biz_data;
