#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh


DS_FILENAME=wegingen
ZIP_FILE=$DS_FILENAME.zip
OBJECTSTORE_PATH=afval/$ZIP_FILE

echo "Download file from objectstore and unzipping"
PYTHONPATH=${SCRIPT_DIR}/../.. python ${SCRIPT_DIR}/../../utils/get_objectstore_file.py $OBJECTSTORE_PATH
unzip $TMPDIR/$ZIP_FILE -d ${TMPDIR}


echo "Create tables & import data"

psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
DROP SCHEMA IF EXISTS his CASCADE;
CREATE SCHEMA his;
COMMIT;
SQL

psql -X --set ON_ERROR_STOP=on < ${TMPDIR}/wegingen.backup

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS afvalwegingen RENAME TO afvalwegingen_old;
ALTER TABLE his.wvt_afv_weeggegevens SET SCHEMA public;
ALTER TABLE wvt_afv_weeggegevens RENAME TO afvalwegingen;
DROP TABLE IF EXISTS afvalwegingen_old;
-- ALTER INDEX asbest_daken_new_pk RENAME TO asbest_daken_pk;
ALTER INDEX wvt_afv_weeggegevens_sidx_geo_geometry RENAME TO afvalwegingen_wkb_geometry_geom_idx;

COMMIT;
SQL


source ${SHARED_DIR}/import/after.sh

