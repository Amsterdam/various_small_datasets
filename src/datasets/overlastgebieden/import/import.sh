#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$SCRIPT_DIR/../..:$SCRIPT_DIR/../../.."
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh

echo "Download file from objectstore"
python $SHARED_DIR/utils/get_objectstore_file.py "overlastgebieden/OOV_gebieden_totaal.dbf"
python $SHARED_DIR/utils/get_objectstore_file.py "overlastgebieden/OOV_gebieden_totaal.prj"
python $SHARED_DIR/utils/get_objectstore_file.py "overlastgebieden/OOV_gebieden_totaal.shp"
python $SHARED_DIR/utils/get_objectstore_file.py "overlastgebieden/OOV_gebieden_totaal.shx"

ogr2ogr -f "PGDump" -t_srs EPSG:28992 -skipfailures -nln overlastgebieden_new ${TMPDIR}/overlastgebieden.sql ${TMPDIR}/OOV_gebieden_totaal.shp
iconv -f iso-8859-1 -t utf-8  ${TMPDIR}/overlastgebieden.sql > ${TMPDIR}/overlastgebieden.utf8.sql

echo "Create tables & import data"
psql -X --set ON_ERROR_STOP=on <<SQL
\i ${TMPDIR}/overlastgebieden.utf8.sql
-- remove entries without geometry
DELETE FROM overlastgebieden_new WHERE wkb_geometry is null;
-- insert polygons valid, as duplicate, unpacking them where needed
INSERT INTO overlastgebieden_new (wkb_geometry, oov_naam, type, url)
SELECT b.geom wkb_geometry, oov_naam, type, url FROM
(
    SELECT oov_naam, type, url, (ST_Dump(ST_CollectionExtract(ST_MakeValid(ST_Multi(wkb_geometry)), 3))).geom as geom FROM
    (
        SELECT * FROM overlastgebieden_new WHERE ST_IsValid(wkb_geometry) = false
    ) a
) b;
-- remove invalid polygons (duplicates were inserted in previous statement)
DELETE FROM overlastgebieden_new WHERE ST_IsValid(wkb_geometry) = false;
SQL

echo "Check imported data"
${SCRIPT_DIR}/check_imported_data.py

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS overlastgebieden RENAME TO overlastgebieden_old;
ALTER TABLE overlastgebieden_new RENAME TO overlastgebieden;
DROP TABLE IF EXISTS overlastgebieden_old;
ALTER INDEX overlastgebieden_new_pk RENAME TO overlastgebieden_pk;
ALTER INDEX overlastgebieden_new_wkb_geometry_geom_idx RENAME TO overlastgebieden_wkb_geometry_geom_idx;
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
