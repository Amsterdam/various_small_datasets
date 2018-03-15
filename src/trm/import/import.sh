#!/usr/bin/env bash

# Convert Tram Metro Data to sql files and import in TRM_ tables

set -e   # stop on any error

CUR_DIR=`pwd`
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SCRIPT_DIR

DATABASE_HOST=${DATABASE_HOST:-localhost}
DATABASE_PORT=${DATABASE_PORT:-5408}
DATABASE_NAME=${DATABASE_NAME:-various_small_datasets}
DATABASE_USER=${DATABASE_USER:-various_small_datasets}
DATABASE_PASSWORD=${DATABASE_PASSWORD:-insecure}

# Register database credentials
export PGPASSFILE=~/.pgpass_various_small_datasets
CREDENTIALS="${DATABASE_HOST}:${DATABASE_PORT}:${DATABASE_NAME}:${DATABASE_USER}:${DATABASE_PASSWORD}"
echo $CREDENTIALS > ${PGPASSFILE}
chmod 600 ${PGPASSFILE}

TMPDIR=/tmp/trm

# Move to trm directory
cd ..
mkdir -p ${TMPDIR}
unzip data/Tram\ KGEs.zip -d ${TMPDIR}
unzip data/Metro\ KGEs.zip -d ${TMPDIR}

# Convert Shape files to PostGIS SQL dump file
ogr2ogr -f "PGDump" ${TMPDIR}/trm_tram.sql ${TMPDIR}/KGE_hartlijnen_Amsterdam_2.050.shp
ogr2ogr -f "PGDump" ${TMPDIR}/trm_metro.sql ${TMPDIR}/Metro\ KGEs.shp

# Convert SQL file to utf-8 SQL file
iconv -f iso-8859-1 -t utf-8  ${TMPDIR}/trm_tram.sql > ${TMPDIR}/trm_tram.utf8.sql
iconv -f iso-8859-1 -t utf-8  ${TMPDIR}/trm_metro.sql > ${TMPDIR}/trm_metro.utf8.sql

# Replace table names
sed -i -- 's/KGE_hartlijnen_Amsterdam_2/public/g' ${TMPDIR}/trm_tram.utf8.sql
sed -i -- 's/"050/"trm_tram/g' ${TMPDIR}/trm_tram.utf8.sql
sed -i -- "s/'050/'trm_tram/g" ${TMPDIR}/trm_tram.utf8.sql

sed -i -- 's/metro kges/trm_metro/g' ${TMPDIR}/trm_metro.utf8.sql

# Replace LINESTRING with GEOMETRY because the data also contains MULTILINESTRING elements
sed -i -- "s/'LINESTRING'/'GEOMETRY'/g" ${TMPDIR}/trm_metro.utf8.sql
sed -i -- "s/'LINESTRING'/'GEOMETRY'/g" ${TMPDIR}/trm_tram.utf8.sql

# Replace column names with spaces
sed -i -- 's/"baanvak in"/"baanvak_in"/g; s/"baanvak _1"/"baanvak_1"/g; s/"lijnnrs aa"/"lijnnrs_aa"/g' ${TMPDIR}/trm_tram.utf8.sql

# Replace HTML entities
sed -i -- 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g;' ${TMPDIR}/trm_tram.utf8.sql

cat ${TMPDIR}/trm_tram.utf8.sql | psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} ${DATABASE_NAME}
cat ${TMPDIR}/trm_metro.utf8.sql | psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} ${DATABASE_NAME}

psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} ${DATABASE_NAME} -c "SELECT UpdateGeometrySRID('trm_tram', 'wkb_geometry', 28992);"
psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} ${DATABASE_NAME} -c "SELECT UpdateGeometrySRID('trm_metro', 'wkb_geometry', 28992);"

rm -Rf ${TMPDIR}

cd $CUR_DIR