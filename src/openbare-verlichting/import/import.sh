#!/usr/bin/env bash

set -u # crash on missing env
set -e # stop on any error

: $HTTP_PROXY  # noop command, simply check if env variable exists

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh
source ${SHARED_DIR}/import/function/publish.sh

set -x # show commands

export PYTHONPATH=${SCRIPT_DIR}/../..

echo "Fetch source data"
wget -e use_proxy=on -O ${TMPDIR}/objects-source.json $OPENBARE_VERLICHTING_DATA_SRC
wget -e use_proxy=on -O ${TMPDIR}/objects-types.json $OPENBARE_VERLICHTING_DATA_TYPES_SRC


echo "Process import data"
python ${SCRIPT_DIR}/json2geojson.py ${TMPDIR}/objects-source.json ${TMPDIR}/objects-types.json ${TMPDIR}/objects.geo.json


echo "Geojson to sql"
# Using PG_USE_COPY for significantly faster processing (several orders)
# see: https://www.gdal.org/drv_pgdump.html
ogr2ogr --config PG_USE_COPY YES -f PGDump -nln openbare_verlichting_new ${TMPDIR}/objects.sql ${TMPDIR}/objects.geo.json


echo "Importing SQL to database"
psql -X --set ON_ERROR_STOP=on -f ${TMPDIR}/objects.sql


echo "Check imported data"
python ${SCRIPT_DIR}/check_imported_data.py

echo "Rename/publish table"
publish_table openbare_verlichting


source ${SHARED_DIR}/import/after.sh
