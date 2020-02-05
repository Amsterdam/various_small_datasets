#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$SCRIPT_DIR/../..:$SCRIPT_DIR/../../.."
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh

ENVIRONMENT=${DATAPUNT_ENVIRONMENT:-acceptance}


DS_FILENAME=bb_quotum.sql
OBJECTSTORE_PATH=bed_and_breakfast/${ENVIRONMENT}/${DS_FILENAME}

echo "Download file from objectstore"
python $SHARED_DIR/utils/get_objectstore_file.py "$OBJECTSTORE_PATH"

egrep -v "^ALTER TABLE.*OWNER TO" ${TMPDIR}/${ENVIRONMENT}/${DS_FILENAME} > ${TMPDIR}/bb_quotum_new.sql
perl -pi -e "s/bb_quotum/bb_quotum_new/g" ${TMPDIR}/bb_quotum_new.sql

psql -X --set ON_ERROR_STOP=on << SQL
BEGIN;
DROP TABLE IF EXISTS bb_quotum_new;
\i ${TMPDIR}/bb_quotum_new.sql;
CREATE INDEX ON public.bb_quotum_new USING gist (geo);
ALTER TABLE public.bb_quotum_new ADD PRIMARY KEY(wijk);
COMMIT;
SQL

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS bb_quotum RENAME TO bb_quotum_old;
ALTER TABLE bb_quotum_new RENAME TO bb_quotum;
DROP TABLE IF EXISTS bb_quotum_old;
ALTER INDEX bb_quotum_new_pkey RENAME TO bb_quotum_pkey;
ALTER INDEX bb_quotum_new_geo_idx RENAME TO bb_quotum_geo_idx;
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
