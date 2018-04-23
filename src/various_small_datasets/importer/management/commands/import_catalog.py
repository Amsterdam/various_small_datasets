import logging
import os
import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from various_small_datasets.catalog.models import DataSet, DataSetField, MapLayer

from django.core.management import BaseCommand

log = logging.getLogger(__name__)


def import_catalog_json_file(filepath):
    with open(filepath) as json_file:
        json_data = json.load(json_file)
        print(json_data)
        for dataset_json in json_data['datasets']:
            fields = dataset_json.pop('fields')
            layers = dataset_json.pop('map_layers', None)
            with transaction.atomic():
                try:
                    existing_dataset = DataSet.objects.get(name=dataset_json['name'])
                    existing_dataset.delete()
                except ObjectDoesNotExist:
                    pass
                dataset = DataSet(**dataset_json)
                dataset.save()
                for field in fields:
                    field['dataset'] = dataset
                    ds_field = DataSetField(**field)
                    ds_field.save()
                if dataset.enable_maplayer:
                    for layer in layers:
                        layer['dataset'] = dataset
                        ds_layer = MapLayer(**layer)
                        ds_layer.save()


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        log.info("Import catalog")
        # Find *.json files in various_small_datasets/catalog/data
        data_dir = "various_small_datasets/catalog/data"
        for file in os.listdir(data_dir):
            if file.endswith(".json"):
                log.info("Import catalog file %s", file)
                import_catalog_json_file(data_dir + '/' + file)
                log.info("End import catalog file %s", file)
