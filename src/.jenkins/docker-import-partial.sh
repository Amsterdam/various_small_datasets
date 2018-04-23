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
    python hior/import.sh
    ;;
esac
done