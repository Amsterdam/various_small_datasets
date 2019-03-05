#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh

echo "Process import data"

ogr2ogr -f "PGDump" -t_srs EPSG:28992 -nln winkgeb_new  ${TMPDIR}/winkgeb.sql ${DATA_DIR}/winkgeb2018.TAB

echo "Create tables & import data for winkel gebieden"
psql -X --set ON_ERROR_STOP=on <<SQL
\i ${TMPDIR}/winkgeb.sql
BEGIN;
\i ${DATA_DIR}/colormap.sql
COMMIT;
SQL

PYTHONPATH=${SCRIPT_DIR}/../.. ${SCRIPT_DIR}/check_imported_data.py

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS winkgeb RENAME TO winkgeb_old;
ALTER TABLE winkgeb_new RENAME TO winkgeb;
DROP TABLE IF EXISTS winkgeb_old CASCADE;
ALTER INDEX winkgeb_new_pk RENAME TO winkgeb_pk;
ALTER INDEX winkgeb_new_wkb_geometry_geom_idx RENAME TO winkgeb_wkb_geometry_geom_idx;
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
