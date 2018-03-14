# various_small_datasets

Code for various small datasets where data does not change very often 

`docker-compose up -d database`

# Bedrijfsinvesteringszone (BIZ)

`echo 0.0.0.0:5408:various_small_datasets:various_small_datasets:insecure >> ~/.pgpass
chmod 600 ~/.pgpass`

`cd biz`

## Convert MapInfo files to PostGIS SQL dump file
`ogr2ogr -f "PGDump" tmp/BIZZONES.sql data/BIZZONES.shp`

## Convert SQL file to utf-8 SQL file
`iconv -f iso-8859-1 -t utf-8  tmp/BIZZONES.sql tmp/BIZZONES.utf8.sql`

## Create SQL insert file 
`python import/convert_data.py`

## Run import for biz 


import/import.sh

# Tram & Metro 

Import data with :
 
`src/trm/import/import.sh `
