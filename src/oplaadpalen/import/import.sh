#!/usr/bin/env bash

# Import oplaadpalen from SOAP API

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh


echo "Process import data"
python ${SCRIPT_DIR}/import_oplaadpalen.py ${TMPDIR}/insert_oplaadpalen.sql


echo "Create tables & import data "
psql -X --set ON_ERROR_STOP=on <<SQL
\i ${SCRIPT_DIR}/oplaadpalen_create.sql
BEGIN;
\i ${TMPDIR}/insert_oplaadpalen.sql
COMMIT;
SQL

PYTHONPATH=${SCRIPT_DIR}/../.. ${SCRIPT_DIR}/check_imported_data.py

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS oplaadpalen RENAME TO oplaadpalen_old;
ALTER TABLE oplaadpalen_new RENAME TO oplaadpalen;
DROP TABLE IF EXISTS oplaadpalen_old;
ALTER INDEX oplaadpalen_new_pkey RENAME TO oplaadpalen_pkey;
ALTER INDEX oplaadpalen_new_wkb_geometry_geom_idx RENAME TO oplaadpalen_wkb_geometry_geom_idx;
ALTER TABLE oplaadpalen RENAME CONSTRAINT cs_external_id_unique_new TO cs_external_id_unique;
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
