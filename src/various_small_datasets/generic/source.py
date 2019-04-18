from urllib import request

from geojson import loads, FeatureCollection
import csv


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


class CSVSourceReader:
    def __init__(self, source_def):
        self.source_type = source_def['source']['type']
        self.source_location = source_def['source']['location']
        self.delimiter = source_def['source']['delimiter']

    def get_source(self):
        if self.source_type == 'file':
            with open(self.source_location) as file:
                csvreader = list(csv.reader(file, delimiter=self.delimiter))
                headers = csvreader[0]
                rows = [dict(zip(headers, row)) for row in csvreader[1:]]
            return rows
        else:
            raise NotImplementedError


def get_source(source_def):
    if source_def['type'] == "GeoJSON":
        return GeoJSONSourceReader(source_def).get_source()
    if source_def['type'] == "csv":
        return CSVSourceReader(source_def).get_source()
    else:
        raise NotImplementedError
