import logging
from django.contrib.gis.geos import GEOSGeometry, Point

from various_small_datasets.generic.catalog import get_model_def, get_import_def, get_dataset_def
from various_small_datasets.generic.check import check_import
from various_small_datasets.generic.db import create_new_datatable, roll_over_datatable
from various_small_datasets.generic.model import get_django_model, represent_field
from various_small_datasets.generic.source import get_source
from various_small_datasets.generic.transform import datetime_from_string, geometry_from_geojson, \
    geometry_from_rd_geojson, geometry_from_api

log = logging.getLogger(__name__)


def convert_coords_srid(coords, source_srid, target_srid):
    p = Point(coords[0], coords[1], srid=source_srid)
    p.transform(target_srid)
    return [p.x, p.y]


def convert_coord_arrays(coords, source_srid, target_srid):
    if not isinstance(coords[0], list):
        return convert_coords_srid(coords, source_srid, target_srid)
    else:
        return [convert_coord_arrays(c, source_srid, target_srid) for c in coords]


def convert_geojson_srid(geojson, source_srid, target_srid):
    if isinstance(geojson, dict):
        if 'coordinates' in geojson:
            geojson['coordinates'] = convert_coord_arrays(geojson['coordinates'], source_srid, target_srid)
            return geojson
        else:
            return {k: convert_geojson_srid(v, source_srid, target_srid) for k, v in geojson.items()}
    elif isinstance(geojson, list):
        return [convert_geojson_srid(i) for i in geojson]
    return geojson


class DictImporter(object):
    def __init__(self, import_def, model_def):
        self.import_def = import_def
        self.model_def = model_def

    def import_data(self, source):
        model = get_django_model(self.import_def['target'], self.model_def, new_table=True)
        for entry in source:
            fields = {}
            for mapping in self.import_def['mapping']['mappings']:
                fields[mapping['target']] = self.expand_transform(entry, mapping, mapping['target'])

            model(**fields).save()

    def expand_transform(self, entry, mapping, target):
        if 'transform' in mapping and mapping['source'] == "transformation":
            source = self.expand_transform(entry, mapping['transform'], target)
        else:
            source = self._get_source(entry, mapping['source'])

        if 'transform' in mapping:
            field_repr = represent_field(target, self.model_def[target])
            source = self._transform(mapping['transform'], source, field_repr)

        return source

    @staticmethod
    def _get_source(entity, path):
        def _recurse_dict(sub_dict, path):
            if len(path) == 1:
                return sub_dict.get(path[0], None)
            else:
                return _recurse_dict(sub_dict.get(path[0], None), path[1:])

        return _recurse_dict(entity, path.split('.'))

    @staticmethod
    def _transform(transform_def, source, field_repr):
        transformations = {
            'time_from_string': datetime_from_string,
            'date_from_string': datetime_from_string,
            'geometry_from_geojson': geometry_from_geojson,
            'geometry_from_rd_geojson': geometry_from_rd_geojson,
            'geometry_from_api': geometry_from_api
        }
        transform = transform_def['type']
        if transform not in transformations:
            raise NotImplementedError
        transformation = transformations[transform]

        return transformation(transform_def, source, field_repr)


class GeoJSONImporter(DictImporter):
    def import_data(self, source):
        super().import_data(source['features'])


class CSVImporter(DictImporter):
    @staticmethod
    def _get_source(entity, path):
        return entity[path]


def do_import(dataset_name):
    model_def = get_model_def(dataset_name)
    import_def = get_import_def(dataset_name)
    source_def = get_dataset_def(dataset_name)

    create_new_datatable(import_def['target'], model_def)

    source = get_source(source_def)

    if source_def['type'] == "GeoJSON":
        importer = GeoJSONImporter(import_def, model_def)
    elif source_def['type'] == "JSON":
        importer = DictImporter(import_def, model_def)
    elif source_def['type'] == "csv":
        importer = CSVImporter(import_def, model_def)
    else:
        raise NotImplementedError

    importer.import_data(source)

    check_import(import_def, model_def)

    roll_over_datatable(import_def['target'], model_def)
