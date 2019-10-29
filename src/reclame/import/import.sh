#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh


DS_FILENAME=reclame-tarief-gebieden
ZIP_FILE=$DS_FILENAME.zip
OBJECTSTORE_PATH=reclame/$ZIP_FILE

echo "Download file from objectstore"
PYTHONPATH=${SCRIPT_DIR}/../.. python ${SCRIPT_DIR}/../../utils/get_objectstore_file.py $OBJECTSTORE_PATH
unzip $TMPDIR/$ZIP_FILE -d ${TMPDIR}

echo "Extracting reclame data"
ogr2ogr -f "PGDump" -t_srs EPSG:28992 -nln reclame_new ${TMPDIR}/reclame.sql ${TMPDIR}/Reclame_tariefgebieden.shp

iconv -f iso-8859-1 -t utf-8  ${TMPDIR}/reclame.sql > ${TMPDIR}/reclame.utf8.sql
# TODO: fix ID rename:
echo "Create tables & import data"
psql -X --set ON_ERROR_STOP=on <<SQL
\i ${TMPDIR}/reclame.utf8.sql
SQL

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;

ALTER TABLE IF EXISTS reclame RENAME TO reclame_old;
ALTER TABLE reclame_new RENAME TO reclame;
DROP TABLE IF EXISTS reclame_old;
ALTER INDEX reclame_new_pk RENAME TO reclame_pk;
ALTER INDEX reclame_new_wkb_geometry_geom_idx RENAME TO reclame_wkb_geometry_geom_idx;

COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
