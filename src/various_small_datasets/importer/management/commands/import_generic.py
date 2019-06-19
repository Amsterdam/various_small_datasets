import logging

from django.core.management import BaseCommand

from various_small_datasets.generic.catalog import generic_importable
from various_small_datasets.generic.import_data import do_import

log = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-d', type=str,
                            help=f"Name of generic dataset to import.\n\nOne of: ({', '.join(generic_importable)})")

    def handle(self, *args, **options):
        dataset_to_import = options['d']

        for dataset in generic_importable:
            if dataset_to_import is None or dataset == dataset_to_import:
                try:
                    do_import(dataset)
                except RuntimeError as e:
                    log.error(f"importing dataset '{dataset}' failed: " + str(e))
