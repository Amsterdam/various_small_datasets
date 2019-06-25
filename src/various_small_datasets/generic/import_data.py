import logging
import time

from various_small_datasets.generic.catalog import get_model_def, get_import_def, get_dataset_def
from various_small_datasets.generic.check import check_import
from various_small_datasets.generic.db import create_new_datatable, roll_over_datatable
from various_small_datasets.generic.model import get_django_model, represent_field
from various_small_datasets.generic.source import get_source
from various_small_datasets.generic.transform import datetime_from_string, geometry_from_geojson, \
    geometry_from_rd_geojson, geometry_from_api, check_integer_or_null, string_from_api, clear_cache

log = logging.getLogger(__name__)


class DictImporter(object):
    def __init__(self, import_def, model_def):
        self.import_def = import_def
        self.model_def = model_def

    def import_data(self, source):
        model = get_django_model(self.import_def['target'], self.model_def, new_table=True)
        count = 0
        prev_time = time.time()

        for entry in source:
            clear_cache()
            fields = {}
            for mapping in self.import_def['mapping']['mappings']:
                fields[mapping['target']] = self.expand_transform(entry, mapping, mapping['target'])

            if not any(fields.values()):
                continue

            model(**fields).save()
            count += 1
            now_time = time.time()
            if now_time - prev_time > 10.0:  # Report every 10 seconds
                prev_time = now_time
                log.info(f"Processed {count} entries...")

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
            'geometry_from_api': geometry_from_api,
            'check_integer_or_null': check_integer_or_null,
            'string_from_api': string_from_api
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
