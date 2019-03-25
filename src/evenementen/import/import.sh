#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh

curl -X GET https://evenementen.amsterdam.nl/?geojson=true\&pager_rows=5000 > ${TMPDIR}/evenementen.json

ogr2ogr -f "PGDump" -t_srs EPSG:28992 -s_srs EPSG:4326  -nln evenementen_new ${TMPDIR}/evenementen.sql ${TMPDIR}/evenementen.json

echo "Create tables & import data for evenementen"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
DROP TABLE IF EXISTS evenementen_new;
COMMIT;
\i ${TMPDIR}/evenementen.sql
SQL

PYTHONPATH=${SCRIPT_DIR}/../.. ${SCRIPT_DIR}/check_imported_data.py

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS evenementen RENAME TO evenementen_old;
ALTER TABLE evenementen_new RENAME TO evenementen;
DROP TABLE IF EXISTS evenementen_old CASCADE;
CREATE UNIQUE INDEX evenementen_idx ON evenementen (ogc_fid);
CREATE INDEX evenementen_gix ON evenementen USING GIST (wkb_geometry);
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh