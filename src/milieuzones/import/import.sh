#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh

echo "Process import data for milieuzones"

python ${SCRIPT_DIR}/json2geojson.py ${DATA_DIR}/milieuzones.json ${TMPDIR}/milieuzones.geo.json
ogr2ogr -f "PGDump"  -t_srs EPSG:28992 -s_srs EPSG:4326 -nln milieuzones_new ${TMPDIR}/milieuzones.sql ${TMPDIR}/milieuzones.geo.json

echo "Create tables & import data for milieuzones"
psql -X --set ON_ERROR_STOP=on <<SQL
\i ${TMPDIR}/milieuzones.sql
SQL

echo "Check imported data for milieuzones"
PYTHONPATH=${SCRIPT_DIR}/../.. ${SCRIPT_DIR}/check_imported_data.py

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS milieuzones RENAME TO milieuzones_old;
ALTER TABLE milieuzones_new RENAME TO milieuzones;
DROP TABLE IF EXISTS milieuzones_old;
ALTER INDEX milieuzones_new_pk RENAME TO milieuzones_pk;
ALTER INDEX milieuzones_new_wkb_geometry_geom_idx RENAME TO milieuzones_wkb_geometry_geom_idx;
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
