import logging
from datetime import datetime
import requests
import json

from geomet import wkt
from django.contrib.gis.geos import GEOSGeometry

log = logging.getLogger(__name__)


def datetime_from_string(transform_def, source, _):
    if source is None:
        return None
    date = datetime.strptime(source, transform_def['properties']['pattern'])
    if transform_def['type'] == "time_from_string":
        return str(date.time())
    return date


def geometry_from_geojson(_, source, field_repr):
    if source is None:
        return None
    source_srid = 4326  # as per GeoJSON standard
    target_srid = field_repr.srid
    geometry = GEOSGeometry(str(source), srid=source_srid)
    geometry.transform(target_srid)
    return geometry


def geometry_from_rd_geojson(_, source, field_repr):
    if source is None:
        return None
    source_srid = 28992
    target_srid = field_repr.srid
    wkt_s = wkt.dumps(source, decimals=4)
    geometry = GEOSGeometry(wkt_s, srid=source_srid)
    geometry.transform(target_srid)
    return geometry


def geometry_from_api(transform_def, source, _):
    if source is None:
        return None
    url = transform_def['url_pattern'].format(id=source)
    with requests.get(url) as response:
        if response.status_code == 200:
            return json.loads(response.content)[transform_def['field']]
        return None
