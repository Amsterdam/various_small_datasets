# various_small_datasets

Code for various small datasets where data does not change very often 

`docker-compose up -d database`

# Migrate Django catalog model

`cd src
python manage.py migrate
`

# Bedrijfsinvesteringszone (BIZ)

Import data with :

`src/biz/import/import.sh`
`src/biz/import/import.sh`

# Tram & Metro (TRM)

Import data with :
 
`src/trm/import/import.sh `

# Import JSON data for catalog (description of BIZ dataset)

`cd src 
python manage.py import_catalog
`
