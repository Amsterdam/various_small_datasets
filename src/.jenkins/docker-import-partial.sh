#!/usr/bin/env bash

set -u   # crash on missing env variables
set -e   # stop on any error

for i in "$@"
do
case $i in
    migrate)
    echo "Migrating db"
    yes yes | python ./manage.py migrate --noinput
    ;;
    biz)
    echo "Importing BIZ"
    biz/import/import.sh
    ;;
    trm)
    echo "Importing TRM"
    trm/import/import.sh
    ;;
    catalog)
    echo "Importing catalog"
    python ./manage.py import_catalog
    ;;
    hior)
    echo "Importing HIOR"
    hior/importer/import.sh
    ;;
    iot)
    echo "Importing IOT"
    iot/import/import.sh
    ;;
    oplaadpalen)
    echo "Importing Oplaadpalen"
    oplaadpalen/import/import.sh
    ;;
    hoofdroutes)
    echo "Importing Hoofdroutes"
    hoofdroutes/import/import.sh
    ;;
    milieuzones)
    echo "Importing Mileuzones"
    milieuzones/import/import.sh
    ;;
    vezips)
    echo "Importing Verzinkbare palen"
    vezips/import/import.sh
    ;;
    winkgeb)
    echo "Importing Winkel gebieden"
    winkgeb/import/import.sh
    ;;
    evenementen)
    echo "Importing Evenementen"
    evenementen/import/import.sh
    ;;
    *)
    echo "Trying to import GeoJSON dataset $i"
    python ./manage.py import_geojson -d $i
    ;;
esac
done