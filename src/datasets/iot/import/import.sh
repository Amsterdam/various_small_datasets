#!/usr/bin/env bash

export SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export SHARED_DIR=${SCRIPT_DIR}/../../shared

source ${SHARED_DIR}/import/config.sh
source ${SHARED_DIR}/import/before.sh

rm -f "${TMPDIR}/sensors.json"
echo "[" > "${TMPDIR}/sensors.json"
for S in "3D%20sensor" "WiFi%20sensor" "Telcamera"
do
    curl "https://maps.amsterdam.nl/_php/haal_objecten.php?TABEL=CROWDSENSOREN&SELECT=${S}&SELECTIEKOLOM=Soort&THEMA=cmsa&TAAL=en&BEHEER=0&NIEUW=niet" >> "${TMPDIR}/sensors.json"
    echo "," >> "${TMPDIR}/sensors.json"
done
echo "[]]" >> "${TMPDIR}/sensors.json"

echo "Process import data"
python ${SCRIPT_DIR}/import.py "${DATA_DIR}/cameras.xlsx" "${DATA_DIR}/beacons.csv" "${TMPDIR}/sensors.json" ${TMPDIR}

rm -f "${TMPDIR}/sensors.json"

echo "Create tables"
psql -X --set ON_ERROR_STOP=on << SQL
\i ${SCRIPT_DIR}/iot_data_create.sql
SQL

echo "Import data"
psql -X --set ON_ERROR_STOP=on <<SQL
\i ${TMPDIR}/iot_things_new.sql
\i ${TMPDIR}/iot_locations_new.sql
SQL

echo "Rename tables"
psql -X --set ON_ERROR_STOP=on <<SQL
BEGIN;
ALTER TABLE IF EXISTS iot_things RENAME TO iot_things_old;
ALTER TABLE IF EXISTS iot_locations RENAME TO iot_locations_old;
ALTER TABLE IF EXISTS iot_owners RENAME TO iot_owners_old;
ALTER VIEW IF EXISTS iot_markers RENAME TO iot_markers_old;

ALTER TABLE iot_things_new RENAME TO iot_things;
ALTER TABLE iot_locations_new RENAME TO iot_locations;
ALTER TABLE iot_owners_new RENAME TO iot_owners;
ALTER VIEW iot_markers_new RENAME TO iot_markers;

DROP TABLE IF EXISTS iot_owners_old CASCADE;
DROP TABLE IF EXISTS iot_locations_old CASCADE;
DROP TABLE IF EXISTS iot_things_old CASCADE;
DROP VIEW IF EXISTS iot_markers_old;
COMMIT;
SQL

source ${SHARED_DIR}/import/after.sh
