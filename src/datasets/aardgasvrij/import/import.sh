#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$SCRIPT_DIR/../..:$SCRIPT_DIR/../../.."
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh

ENVIRONMENT=${DATAPUNT_ENVIRONMENT:-acceptance}

DS_FILENAME=Export_cartograaf_20200604.zip
OBJECTSTORE_PATH=aardgasvrij/${DS_FILENAME}

echo "Download file from objectstore"
python $SHARED_DIR/utils/get_objectstore_file.py "$OBJECTSTORE_PATH"
unzip -j -d ${TMPDIR}  ${TMPDIR}/${DS_FILENAME}

ogr2ogr -f "PGDump" -t_srs EPSG:28992 -nlt PROMOTE_TO_MULTI -nln buurten_new ${TMPDIR}/buurten.sql ${TMPDIR}/buurten_na_inspraak.shp
iconv -f iso-8859-1 -t utf-8  ${TMPDIR}/buurten.sql > ${TMPDIR}/buurten.utf8.sql

ogr2ogr -f "PGDump" -t_srs EPSG:28992 -nln buurtinitiatieven_new ${TMPDIR}/buurtinitiatieven.sql ${TMPDIR}/buurtinitiatieven.shp
iconv -f iso-8859-1 -t utf-8  ${TMPDIR}/buurtinitiatieven.sql > ${TMPDIR}/buurtinitiatieven.utf8.sql

psql -X --set ON_ERROR_STOP=on << SQL
DROP TABLE IF EXISTS buurten_new, buurtinitiatieven_new CASCADE;
\i ${TMPDIR}/buurten.sql;
\i ${TMPDIR}/buurtinitiatieven.sql;
SQL

${SCRIPT_DIR}/check_imported_data.py

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
DROP TABLE IF EXISTS buurten, buurtinitiatieven CASCADE;
ALTER TABLE buurten_new RENAME TO buurten;
ALTER TABLE buurtinitiatieven_new RENAME TO buurtinitiatieven;
ALTER INDEX buurten_new_pk RENAME TO buurten_pk;
ALTER INDEX buurten_new_wkb_geometry_geom_idx RENAME TO buurten_wkb_geometry_geom_idx;
ALTER INDEX buurtinitiatieven_new_pk RENAME TO buurtinitiatieven_pk;
ALTER INDEX buurtinitiatieven_new_wkb_geometry_geom_idx RENAME TO buurtinitiatieven_wkb_geometry_geom_idx;
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
