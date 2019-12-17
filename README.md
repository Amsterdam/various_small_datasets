# various_small_datasets

Code for various small datasets where data does not change very often

# Requirements

    Python >= 3.7
    GDAL (OSX: brew install gdal)

# Preparation

    mkdir ~/.ssh/datapunt.key
    python3 -m venv venv
    source venv/bin/activate
    pip install -r src/requirements.txt

    docker-compose up -d database

# Migrate Django catalog model

    cd src
    python manage.py migrate
    python manage.py import_catalog           # Processes src/various_small_datasets/catalog/data
    python manage.py import_generic           # Processes evenementen + vastgoed

Get access to objectstore (see password manager):

    export VSD_OBJECTSTORE_PROJECTNAME=...
    export VSD_OBJECTSTORE_PROJECTID=...
    export VSD_OBJECTSTORE_USER=...
    export VSD_OBJECTSTORE_PASSWORD=...

Import all remaining datasets:

    src/afvalwegingen/import/import.sh
    src/asbest/import/import.sh
    src/bekendmakingen/import/import.sh
    src/biz/import/import.sh                   # Bedrijfsinvesteringszone (BIZ)
    src/hior/importer/import.sh                # Handboek Inrichting Openbare Ruimte (HIOR)
    src/hoofdroutes/import/import.sh           # Hoofdroutes
    src/iot/import/import.sh
    src/milieuzones/import/import.sh
    src/openbare-verlichting/import/import.sh
    src/oplaadpalen/import/import.sh           # Oplaadpalen
    src/overlastgebieden/import/import.sh
    src/parkeerzones/import/import.sh
    src/reclamebelasting/import/import.sh
    src/trm/import/import.sh                   # Tram & Metro (TRM)
    src/vezips/import/import.sh
    src/vuurwerk/import/import.sh
    src/winkgeb/import/import.sh

# Run the server

    docker-compose up

The server can be reached locally at:

    http://localhost:8000

urls to test are

    /status/health
    /status/data
    /vsd/
    /vsd/biz/
    /vsd/biz/0/
    /vsd/oplaadpalen/?wkb_geometry=123291,487198,500
    /vsd/oplaadpalen/1000/

Filtering on name and geometry field is also supported, although this is not yet  shown in the swagger definition

For example :

    /vsd/biz/?naam=kalverstraat
    /vsd/biz/?geometrie=52.362762,4.907598

# Cookbook for new datasets

Create a directory for the new dataset (ds)

    mkdir src/ds

Create a directory for the import data for the dataset

    mkdir src/ds/data

Put the input data in this directory

Create a directory for the import scripts to process and import the data in the database

    mkdir src/ds/import

The basic process consists of:

    Reading the data
    Process and check the data
    Write the results in a .sql file with insert statements
    Call the import and process the sql insert file in a shell script "import.sh"
        Read data and create sql insert file
        Create tables for new data
        Run sql insert on new tables
        Rename existing tables, rename new tables and then remove any old tables
    Use the shared code in src/shared/import to keep the import shell script as small as possible

When the import is OK include the dataset in the catalog

    Construct a ds.json in src/various_small_datasets/catalog/data/ds.json

    python manage.py import_catalog

    python manage.py runserver

View your new dataset at localhost:8000/vsd/ds

Because we now have multiple datasets in one database we want to be able to add or update only one dataset
without touching or impacting the other datasets. That is why we import initially all the data in "_new" tables
and, if everything went well, finally we rename in one transactions the existing tables to "_old" en the "_new"
tables to the version used by the API.

In this way, nothing is broken if something went wrong before the last step of renaming the tables, and the database
usage for other tables is not in any way impacted (except for some db performance during import).

In Jenkins we also have a special import called "Partial_Import_Various_Small_Datasets_(DEV|PROD)" where we can
do a partial import for only one of the datasets or do a Django migrate or import_catalog if that was changed.
This Jenkins import itself uses the Openstack Ansible playbook "import-various-small-datasets.yml"

# Generate MAP files for MAPSERVER

It is also possible to generate a simple MAP file for MAPSERVER from the specification.

In the JSON file that describes the dataset the following entries should be present :

      "enable_maplayer": true,
      "map_template": "name_of_template"    # Optional default is default.map.template
      "map_title": "Title
      "map_abstract": "Oneline abstract"    # Optional
      "map_layers": [
        {
          "name": "name_of_layer",
          "title": "title_of_layer",
          "abstract": "abstract_for_layer",    # Optional
          "filter": "expression for filter in layer"    # Optional
          "color": "0 70 153",                 # Optional
          "style": "expression for style",     # Optional, overrides color
          "minscale": 10,
          "maxscale": 400000,
          "label": "naam",
          "label_minscale": 10,
          "label_maxscale": 10000
        }
      ],

 If these entries are specified map files are generated with the command:

    cd src
    python manage.py generate_map_files

Make sure that you have run the following:

    python manage.py migrate
    python manage.py import_catalog

Then you can find the generated mapfiles in **various_small_datasets/tools/mapfiles**

Copy these files to the **mapserver**  and test if they work.
