import logging
import os
import json

from django.db import transaction

from various_small_datasets.catalog.models import DataSet, DataSetField

from django.core.management import BaseCommand

log = logging.getLogger(__name__)


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
                with open(data_dir + '/' + file) as json_file:
                    json_data = json.load(json_file)
                    print(json_data)
                    for dataset_json in json_data['datasets']:
                        fields = dataset_json.pop('fields')
                        with transaction.atomic():
                            dataset = DataSet(**dataset_json)
                            dataset.save()
                            for field in fields:
                                field['dataset'] = dataset
                                ds_field = DataSetField(**field)
                                ds_field.save()
                    log.info("End import catalog file %s", file)
