from urllib import request

from geojson import loads, FeatureCollection


class GeoJSONSourceReader:
    def __init__(self, source_def):
        self.source_type = source_def['source']['type']
        self.source_location = source_def['source']['location']

    def get_source(self):
        if self.source_type == 'url':
            with request.urlopen(self.source_location) as response:
                geojson = loads(response.read().decode())
            if not isinstance(geojson, FeatureCollection):
                raise ValueError(f" url '{self.source_location}' didn't return a valid FeatureCollection")
            return geojson
        else:
            raise NotImplementedError


def get_source(source_def):
    if source_def['type'] == "GeoJSON":
        return GeoJSONSourceReader(source_def).get_source()
    else:
        raise NotImplementedError
