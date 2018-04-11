#!/usr/bin/env bash

set -e   # stop on any error
set -u

CUR_DIR=`pwd`
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SCRIPT_DIR

export TMPDIR=/tmp/biz

# Move to biz directory
cd ..
rm -Rf ${TMPDIR}
mkdir -p ${TMPDIR}

echo "Convert data"
ogr2ogr -f "PGDump" ${TMPDIR}/BIZZONES.sql data/BIZZONES.shp
iconv -f iso-8859-1 -t utf-8  ${TMPDIR}/BIZZONES.sql > ${TMPDIR}/BIZZONES.utf8.sql
python import/convert_data.py ${TMPDIR}/BIZZONES.utf8.sql data/Dataset\ BIZ\ v4.xlsx ${TMPDIR}/biz_data_insert.sql

export PGHOST=${DATABASE_HOST_OVERRIDE:-${DATABASE_HOST:-localhost}}
export PGPORT=${DATABASE_PORT_OVERRIDE:-${DATABASE_PORT:-5408}}
export PGDATABASE=${DATABASE_NAME:-various_small_datasets}
export PGUSER=${DATABASE_USER:-various_small_datasets}
export PGPASSWORD=${DATABASE_PASSWORD:-insecure}

psql -X --set ON_ERROR_STOP=on <<SQL
\echo Create new tables
\i import/biz_data_create.sql
\echo Import data
\i ${TMPDIR}/biz_data_insert.sql
\echo Rename tables
BEGIN;
ALTER TABLE IF EXISTS biz_data RENAME TO biz_data_old;
ALTER TABLE biz_data_new RENAME TO biz_data;
DROP TABLE IF EXISTS biz_data_old CASCADE;
ALTER VIEW biz_view_new RENAME TO biz_view;
ALTER INDEX naam_unique_new RENAME TO naam_unique;
ALTER INDEX biz_data_new_wkb_geometry_geom_idx RENAME TO biz_data_wkb_geometry_geom_idx;
COMMIT;
SQL

rm -Rf ${TMPDIR}
cd $CUR_DIR
