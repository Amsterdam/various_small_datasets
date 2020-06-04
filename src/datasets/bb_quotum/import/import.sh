#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$SCRIPT_DIR/../..:$SCRIPT_DIR/../../.."
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh

ENVIRONMENT=${DATAPUNT_ENVIRONMENT:-acceptance}
ENVIRONMENT1=acceptance

DS_FILENAME=bb_quotum.sql
DS_FILENAME1=omzettingen_quotum.sql
OBJECTSTORE_PATH=bed_and_breakfast/${ENVIRONMENT}/${DS_FILENAME}
OBJECTSTORE_PATH1=bed_and_breakfast/${ENVIRONMENT1}/${DS_FILENAME1}

echo "Download files from objectstore"
python $SHARED_DIR/utils/get_objectstore_file.py "$OBJECTSTORE_PATH"
python $SHARED_DIR/utils/get_objectstore_file.py "$OBJECTSTORE_PATH1"

egrep -v "^ALTER TABLE.*OWNER TO|^GRANT SELECT ON" ${TMPDIR}/${ENVIRONMENT}/${DS_FILENAME} > ${TMPDIR}/bb_quotum_new.sql
egrep -v "^ALTER TABLE.*OWNER TO|^GRANT SELECT ON" ${TMPDIR}/${ENVIRONMENT1}/${DS_FILENAME1} > ${TMPDIR}/omzettingen_quotum_new.sql

perl -pi -e "s/quota_bbkaartlaagexport/bb_quotum_new/g" ${TMPDIR}/bb_quotum_new.sql
perl -pi -e "s/quota_omzettingenkaartlaagexport/omzettingen_quotum_new/g" ${TMPDIR}/omzettingen_quotum_new.sql

echo "Import data"
psql -X --set ON_ERROR_STOP=on << SQL
BEGIN;
DROP TABLE IF EXISTS bb_quotum_new CASCADE;
DROP SEQUENCE IF EXISTS bb_quotum_new_id_seq CASCADE;
DROP INDEX IF EXISTS bb_quotum_new_geo_id;
\i ${TMPDIR}/bb_quotum_new.sql;
DROP TABLE IF EXISTS omzettingen_quotum_new CASCADE;
DROP SEQUENCE IF EXISTS omzettingen_quotum_new_id_seq CASCADE;
DROP INDEX IF EXISTS omzettingen_quotum_new_geo_id;
\i ${TMPDIR}/omzettingen_quotum_new.sql;
COMMIT;
SQL

echo "Check data"
${SCRIPT_DIR}/check_imported_data.py

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
-- Bed and breakfast
ALTER TABLE IF EXISTS bb_quotum RENAME TO bb_quotum_old;
ALTER SEQUENCE IF EXISTS bb_quotum_id_seq RENAME TO bb_quotum_old_id_seq;
ALTER TABLE bb_quotum_new RENAME TO bb_quotum;
ALTER SEQUENCE bb_quotum_new_id_seq RENAME TO bb_quotum_id_seq;
DROP TABLE IF EXISTS bb_quotum_old;
DROP SEQUENCE IF EXISTS bb_quotum_old_id_seq CASCADE;
ALTER INDEX bb_quotum_new_pkey RENAME TO bb_quotum_pkey;
ALTER INDEX bb_quotum_new_geo_id RENAME TO bb_quotum_geo_id;
-- Omzettingen
ALTER TABLE IF EXISTS omzettingen_quotum RENAME TO omzettingen_quotum_old;
ALTER SEQUENCE IF EXISTS omzettingen_quotum_id_seq RENAME TO omzettingen_quotum_old_id_seq;
ALTER TABLE omzettingen_quotum_new RENAME TO omzettingen_quotum;
ALTER SEQUENCE omzettingen_quotum_new_id_seq RENAME TO omzettingen_quotum_id_seq;
DROP TABLE IF EXISTS omzettingen_quotum_old;
DROP SEQUENCE IF EXISTS omzettingen_quotum_old_id_seq CASCADE;
ALTER INDEX omzettingen_quotum_new_pkey RENAME TO omzettingen_quotum_pkey;
ALTER INDEX omzettingen_quotum_new_geo_id RENAME TO omzettingen_quotum_geo_id;
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
