import logging
from django.core.management import BaseCommand
from various_small_datasets.geojson.import_geojson import import_geojson
from various_small_datasets.geojson import geojson_api
log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-d', type=str, help="Name of geojson dataset to import")
        parser.add_argument('-f', action='store_true', help="force refresh of data, even if changed too much")

    def handle(self, *args, **options):
        force_refresh = options['f']
        dataset_to_import = options['d']

        for dataset in geojson_api.datasets_config:
            if dataset['source']['type'] != 'url':
                log.warning('importing something other than geojson from url is not implemented yet')
                break

            if dataset_to_import is None or dataset['dataset'] == dataset_to_import:
                try:
                    import_geojson(dataset['source']['value'], dataset['dataset'], force_import=force_refresh)
                except RuntimeError:
                    log.error(f"importing dataset '{dataset['dataset']}' failed: ")

