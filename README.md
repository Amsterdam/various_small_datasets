# various_small_datasets
Code for various small datasets where data does not change very often 

docker-compose up -d database

# Bedrijfsinvesteringszone (BIZ)

echo 0.0.0.0:5408:various_small_datasets:various_small_datasets:insecure >> ~/.pgpass
chmod 600 ~/.pgpass

cd biz

# Convert MapInfo files to PostGIS SQL dump file
ogr2ogr -f "PGDump" tmp/BIZZONES.sql data/BIZZONES.shp

# Convert SQL file to utf-8 SQL file
iconv -f iso-8859-1 -t utf-8  tmp/BIZZONES.sql tmp/BIZZONES.utf8.sql

# Create SQL insert file 
python import/convert_data.py


cat biz_data_create.sql | psql -p 5408 -h 0.0.0.0 -U various_small_datasets various_small_datasets
cat biz_data_insert.sql | psql -p 5408 -h 0.0.0.0 -U various_small_datasets various_small_datasets

cd ..

# Make a backup for the entire various_small_datasets #
mkdir -p backups
pg_dump -Fc -h 0.0.0.0 -p 5408 -U various_small_datasets various_small_datasets > backups/various_small_datasets.dump


# Restore data in some database #
createuser -p 5403 -h 0.0.0.0 -P -U postgres various_small_datasets || echo "Could not create various_small_datasets, continuing"
createuser -p 5403 -h 0.0.0.0 -P -U postgres various_small_datasets_read || echo "Could not create various_small_datasets_read, continuing"

psql -p 5403 -h 0.0.0.0 -U postgres postgres -c "alter user various_small_datasets with password 'insecure';"
psql -p 5403 -h 0.0.0.0 -U postgres postgres -c "alter user various_small_datasets_read with password 'insecure';"

pg_restore -p 5403 -h 0.0.0.0 --if-exists -j 4 -c -C -d postgres -U postgres backups/various_small_datasets.dump

