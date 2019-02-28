import logging
import os
import json

from django.db import transaction

from various_small_datasets.catalog.models import DataSet,  MapLayer

from django.core.management import BaseCommand

log = logging.getLogger(__name__)


def import_dataset_in_db(dataset_json):
    layers = dataset_json.pop('map_layers', None)
    with transaction.atomic():
        dataset = DataSet(**dataset_json)
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
