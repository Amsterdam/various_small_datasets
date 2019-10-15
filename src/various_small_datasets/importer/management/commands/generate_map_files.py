import logging
import os

from various_small_datasets.catalog.models import DataSet
from various_small_datasets.interfaces import json_, amsterdam_schema
from various_small_datasets.generators.mapfile import (
    MapfileGenerator, LegacyMapfileGenerator
)
from various_small_datasets.interfaces.mapfile.serializers import (
    MappyfileSerializer, JinjaSerializer
)
from django.core.management import BaseCommand


log = logging.getLogger(__name__)


def json_loader(file_paths: list):
    for file_path in file_paths:
        with open(file_path, "r") as fh:
            base_uri = (
                "file://" + os.path.dirname(os.path.realpath(file_path)) + "/"
            )
            yield amsterdam_schema.AmsterdamSchema(
                json_.load(fh, base_uri=base_uri)
            )


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--sources', nargs="+", type=str, default=["db"],
            choices=["db", "schema"]
        )
        pass

    def handle(self, *args, **options):
        log.info("Generate map files")
        tools_dir = "various_small_datasets/tools"
        template_dir = tools_dir + "/map_templates"
        map_dir = tools_dir + "/map_files"

        if not os.path.exists(map_dir):
            os.mkdir(map_dir)
        generators = []

        if 'db' in options['sources']:
            generators.append(
                LegacyMapfileGenerator(
                    map_dir=map_dir,
                    serializer=JinjaSerializer(template_dir),
                    datasets=DataSet.objects.filter(  # pylint: disable=no-member
                        enable_maplayer=True
                    )
                )
            )
        if 'schema' in options['sources']:
            generators.append(
                MapfileGenerator(
                    map_dir=map_dir,
                    serializer=MappyfileSerializer(),
                    datasets=json_loader(
                        ["./schemas/asbestdaken/asbest.json"]
                    )
                )
            )

        for generator in generators:
            generator()

        log.info(f"End generating mapfiles, results written to: {map_dir}")
