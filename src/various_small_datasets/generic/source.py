from urllib import request

from geojson import loads, FeatureCollection
import csv
import objectstore
import os

OBJECTSTORE = dict(
    VERSION='2.0',
    AUTHURL='https://identity.stack.cloudvps.com/v2.0',
    TENANT_NAME=os.getenv('VSD_OBJECTSTORE_PROJECTNAME'),
    TENANT_ID=os.getenv('VSD_OBJECTSTORE_PROJECTID'),
    USER=os.getenv('VSD_OBJECTSTORE_USER'),
    PASSWORD=os.getenv('VSD_OBJECTSTORE_PASSWORD'),
    REGION_NAME='NL',
)


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
        self.source_encoding = source_def['source']['encoding']
        self.delimiter = source_def['source']['delimiter']

    def get_source(self):
        if self.source_type == 'objectstore':
            container = self.source_location.split("/")[0]
            path = "/".join(self.source_location.split("/")[1:])

            connection = objectstore.get_connection(OBJECTSTORE)
            file = objectstore.get_object(connection, {'name': path}, container)
            csv_file = file.decode(self.source_encoding).splitlines()

            csvreader = list(csv.reader(csv_file, delimiter=self.delimiter))
            headers = csvreader[0]
            rows = [dict(zip(headers, row)) for row in csvreader[1:]]

            return rows
        elif self.source_type == 'file':
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


def get_objectstore_file(location, dir):
    connection = objectstore.get_connection(OBJECTSTORE)
    container = location.split("/")[0]
    path = "/".join(location.split("/")[1:])
    new_data = objectstore.get_object(connection, {'name': path}, container)
    output_path = dir + path
    with open(output_path, 'wb') as file:
        file.write(new_data)



