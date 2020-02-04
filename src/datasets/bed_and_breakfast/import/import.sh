#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$SCRIPT_DIR/../..:$SCRIPT_DIR/../../.."
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh


DS_FILENAME="2020-02-03 12:44:46.536670+00:00.sql"
OBJECTSTORE_PATH=bed_and_breakfast/acceptance/$DS_FILENAME

echo "Download file from objectstore"
python $SHARED_DIR/utils/get_objectstore_file.py $OBJECTSTORE_PATH

egrep -v "^ALTER TABLE.*OWNER TO" "$DS_FILENAME" > ${TMPDIR}/bed_and_breakfast_new.sql

perl -pi -e "s/public.temp_kaartlaag/public.bed_and_breakfast_new/g" ${TMPDIR}/bed_and_breakfast_new.sql

psql -X --set ON_ERROR_STOP=on << SQL
BEGIN;
\i ${TMPDIR}/bed_and_breakfast_new.sql
COMMIT;
SQL

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS bed_and_breakfast RENAME TO bed_and_breakfast_old;
ALTER TABLE bed_and_breakfast_new RENAME TO bed_and_breakfast;
DROP TABLE IF EXISTS bed_and_breakfast_old;
ALTER INDEX bed_and_breakfast_new_pk RENAME TO bed_and_breakfast_pk;
ALTER INDEX bed_and_breakfast_new_wkb_geometry_geom_idx RENAME TO bed_and_breakfast_wkb_geometry_geom_idx;
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
