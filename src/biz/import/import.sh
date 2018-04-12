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

# TODO : The statement ALTER DEFAULT PRIVILEGES grant SELECT on tables to ${PGUSER}_read; is temporary
# This should probably be fixed in Openstack in roles/with-database/tasks/main.yml
# Replace :
#       shell: psql -U postgres {{ name }} -c 'ALTER DEFAULT PRIVILEGES grant SELECT on tables to {{ name }}_read;'
# with :
#       shell: psql -U postgres {{ name }} -c 'ALTER DEFAULT PRIVILEGES FOR postgres, {{ name}} grant SELECT on tables to {{ name }}_read;
# Same for sequences there
# TODO : Add verification of new tables after creation and insert and before rename. If not verified  the rename should not happen
psql -X --set ON_ERROR_STOP=on <<SQL
ALTER DEFAULT PRIVILEGES grant SELECT on tables to ${PGUSER}_read;
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
