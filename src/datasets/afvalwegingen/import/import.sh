#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$SCRIPT_DIR/../..:$SCRIPT_DIR/../../.."
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh

ENVIRONMENT=${DATAPUNT_ENVIRONMENT:-acceptance}

echo "Drop and create schema"

psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
DROP SCHEMA IF EXISTS pte CASCADE;
CREATE SCHEMA pte;
COMMIT;
SQL

echo "Download and import pgsql dumps"

for ds_filename in afval_weging afval_container afval_cluster
do
    ZIP_FILE=$ENVIRONMENT/$ds_filename.zip
    OBJECTSTORE_PATH=afval/$ZIP_FILE

    echo "Download file from objectstore and unzipping"
    python $SHARED_DIR/utils/get_objectstore_file.py $OBJECTSTORE_PATH
    unzip $TMPDIR/$ZIP_FILE -d ${TMPDIR}

    psql -X --set ON_ERROR_STOP=on < ${TMPDIR}/$ds_filename.backup

done


echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
DROP TABLE IF EXISTS public.afval_weging;
ALTER TABLE pte.afval_weging SET SCHEMA public;
DROP TABLE IF EXISTS public.afval_container;
ALTER TABLE pte.afval_container SET SCHEMA public;
DROP TABLE IF EXISTS public.afval_cluster;
ALTER TABLE pte.afval_cluster SET SCHEMA public;
COMMIT;
SQL


source ${SHARED_DIR}/import/after.sh

