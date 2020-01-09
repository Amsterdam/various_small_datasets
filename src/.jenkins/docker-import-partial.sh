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
    datasets/biz/import/import.sh
    ;;
    trm)
    echo "Importing TRM"
    datasets/trm/import/import.sh
    ;;
    catalog)
    echo "Importing catalog"
    python ./manage.py import_catalog
    ;;
    hior)
    echo "Importing HIOR"
    datasets/hior/importer/import.sh
    ;;
    iot)
    echo "Importing IOT"
    datasets/iot/import/import.sh
    ;;
    oplaadpalen)
    echo "Importing Oplaadpalen"
    datasets/oplaadpalen/import/import.sh
    ;;
    hoofdroutes)
    echo "Importing Hoofdroutes"
    datasets/hoofdroutes/import/import.sh
    ;;
    milieuzones)
    echo "Importing Mileuzones"
    datasets/milieuzones/import/import.sh
    ;;
    vezips)
    echo "Importing Verzinkbare palen"
    datasets/vezips/import/import.sh
    ;;
    winkgeb)
    echo "Importing Winkel gebieden"
    datasets/winkgeb/import/import.sh
    ;;
    evenementen)
    echo "Importing Evenementen"
    python ./manage.py import_generic -d evenementen
    ;;
    bekendmakingen)
    echo "Importing Bekendmakingen"
    datasets/bekendmakingen/import/import.sh
    ;;
    overlastgebieden)
    echo "Import Overlastgebieden"
    datasets/overlastgebieden/import/import.sh
    ;;
    openbare_verlichting)
    echo "Importing Openbare-verlichting"
    datasets/openbare-verlichting/import/import.sh
    ;;
    parkeerzones)
    echo "Import Parkeerzones"
    datasets/parkeerzones/import/import.sh
    ;;
    asbest)
    echo "Import Asbest"
    datasets/asbest/import/import.sh
    ;;
    reclame)
    echo "Import Reclametariefgebieden"
    datasets/reclamebelasting/import/import.sh
    ;;
    vuurwerk)
    echo "Import Vuurwerkvrije zones"
    datasets/vuurwerk/import/import.sh
    ;;
    afvalwegingen)
    echo "Import Afvalwegingen"
    datasets/afvalwegingen/import/import.sh
    ;;
    *)
    echo "Trying to import Generic dataset $i"
    python ./manage.py import_generic -d $i
    ;;
esac
done
