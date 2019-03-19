from urllib import request

from django.contrib.gis.geos import GEOSGeometry
from django.db import connection, DatabaseError
from geojson import loads, FeatureCollection

from various_small_datasets.geojson.geojson_db import create_new_datatable_sql, geojson_model_factory, roll_over_datatable_sql

# Check if the dataset didn't change too much (> 20%)
FRACTION_OFF = 0.2


def _get_feature_id(feature):
    if 'id' in feature and feature['id'] is not None:
        return feature['id']

    possible_id_keys = [k for k in feature['properties'].keys() if k.lower() == 'id']
    if len(possible_id_keys) > 0:
        return feature['properties'].pop(possible_id_keys[0], None)

    return None


def import_geojson(url, dataset_name, force_import=False):
    with request.urlopen(url) as response:
        geojson = loads(response.read().decode())

    if not isinstance(geojson, FeatureCollection):
        raise ValueError(f" url '{url}' didn't return a valid FeatureCollection")

    # Check if the dataset didn't change too much (set with FRACTION_OFF)
    try:
        current_count = geojson_model_factory(dataset_name, new_table=False).objects.count()
        new_count = len(geojson['features'])

        if not (force_import or (1 - FRACTION_OFF) * new_count < current_count < (1 + FRACTION_OFF) * new_count):
            raise RuntimeError(f"Dataset '{dataset_name}' changed too much to import")
    # If current table doesn't exist:
    except DatabaseError:
        pass

    # Import
    sql = create_new_datatable_sql(dataset_name)

    with connection.cursor() as cursor:
        cursor.execute(sql)

    GeoJSONModel = geojson_model_factory(dataset_name, new_table=True)

    for feature in geojson['features']:
        feature = {k.lower(): v for k, v in feature.items()}
        feature_id = _get_feature_id(feature)

        geometry_geojson = str(feature['geometry'])
        geometry = GEOSGeometry(geometry_geojson)

        GeoJSONModel(id=feature_id,
                     geometry=geometry,
                     properties=feature['properties'])\
            .save()

    sql = roll_over_datatable_sql(dataset_name)

    with connection.cursor() as cursor:
        cursor.execute(sql)

