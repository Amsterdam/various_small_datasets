import copy

import logging
import os
import json

from django.db import transaction
from django.core.management import BaseCommand

from various_small_datasets.catalog.models import DataSet,  MapLayer
from various_small_datasets.generic.catalog import generic_importable
from various_small_datasets.generic.legacy import get_legacy_definition

log = logging.getLogger(__name__)


def import_dataset_in_db(dataset_json):
    layers = dataset_json.pop('map_layers', None)

    data = copy.deepcopy(dataset_json)

    # Set default EPSG code for geometry fields
    if data.get('geometry_field', False) and data.get('geometry_epsg') is None:
        data['geometry_epsg'] = 28992

    with transaction.atomic():
        dataset = DataSet(**data)
        dataset.save()
        if dataset.enable_maplayer:
            for layer in layers:
                layer['dataset'] = dataset
                ds_layer = MapLayer(**layer)
                ds_layer.save()


def import_catalog_json_file(filepath):
    with open(filepath) as json_file:
        json_data = json.load(json_file)
        print(json_data)
        for dataset_json in json_data['datasets']:
            import_dataset_in_db(dataset_json)


def import_generic_metadata(dataset):
    data_dict = get_legacy_definition(dataset)

    for dataset_json in data_dict['datasets']:
        import_dataset_in_db(dataset_json)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        log.info("Import catalog")
        # Find *.json files in various_small_datasets/catalog/data
        data_dir = "various_small_datasets/catalog/data"
        DataSet.objects.all().delete()
        for file in os.listdir(data_dir):
            if file.endswith(".json"):
                log.info("Import catalog file %s", file)
                import_catalog_json_file(data_dir + '/' + file)
                log.info("End import catalog file %s", file)

        for dataset in generic_importable:
            log.info(f"Import catalog file for {dataset}")
            import_generic_metadata(dataset)
            log.info(f"End import catalog file for {dataset}")
