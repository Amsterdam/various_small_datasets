import logging
from datetime import datetime
import requests
import json
import os

from geomet import wkt
from django.contrib.gis.geos import GEOSGeometry

datapunt_api_root = os.getenv('DATAPUNT_API_ROOT', 'https://api.data.amsterdam.nl')
log = logging.getLogger(__name__)


def _geometry_from_string(geos_input, source_srid, target_srid):
    geometry = GEOSGeometry(geos_input, srid=source_srid)
    geometry.transform(target_srid)
    return geometry


def geometry_from_geojson(_, source, field_repr):
    if source is None:
        return None

    geos_input = str(source)
    source_srid = 4326  # as per GeoJSON standard
    target_srid = field_repr.srid

    return _geometry_from_string(geos_input, source_srid, target_srid)


def geometry_from_rd_geojson(_, source, field_repr):
    if source is None:
        return None

    geos_input = wkt.dumps(source, decimals=4)
    source_srid = 28992
    target_srid = field_repr.srid

    return _geometry_from_string(geos_input, source_srid, target_srid)


def geometry_from_api(transform_def, source, _):
    if source is None:
        return None
    url = transform_def['url_pattern'].format(api_root=datapunt_api_root, id=source)
    with requests.get(url) as response:
        if response.status_code == 200:
            return json.loads(response.content)[transform_def['field']]
        return None


def datetime_from_string(transform_def, source, _):
    if source is None:
        return None
    date = datetime.strptime(source, transform_def['properties']['pattern'])
    if transform_def['type'] == "time_from_string":
        return str(date.time())
    return date


def check_integer_or_null(transform_def, source, _):
    if source is None or not source.isdigit():
        return None
    return source
