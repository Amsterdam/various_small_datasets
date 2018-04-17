# various_small_datasets

Code for various small datasets where data does not change very often 

# Requirements

    Python >= 3.5

# Preparation

    python3 -m venv venv
    source venv/bin/activate
    pip install -r src/requirements.txt
    
    docker-compose up -d database

# Migrate Django catalog model

    cd src
    python manage.py migrate

# Bedrijfsinvesteringszone (BIZ)

Import data with :

    src/biz/import/import.sh
    src/biz/import/import.sh

# Tram & Metro (TRM)

Import data with :
 
    src/trm/import/import.sh

# Import JSON data for catalog (description of BIZ dataset)

    cd src 
    python manage.py import_catalog

# Run the server

    docker-compose up
    
The server can be reached locally at:

    http://localhost:8000

urls to test are

    /status/health
    /status/data
    /vsd/biz/
    /vsd/biz/0