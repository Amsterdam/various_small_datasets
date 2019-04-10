import logging
import os

from jinja2 import Environment, FileSystemLoader
from various_small_datasets.catalog.models import DataSet
from django.core.management import BaseCommand


log = logging.getLogger(__name__)


def get_map_content(env: Environment, ds):
    ds_dict = ds.__dict__
    # get layers
    ds_dict["layers"] = map(lambda x: x.__dict__, ds.maplayer_set.all())
    ds_dict["id_field"] = ds.pk_field
    if ds.map_template is not None:
        template_file = ds.map_template
    else:
        template_file = 'default.map.template'

    template = env.get_template(template_file)
    return template.render(ds=ds_dict)


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        log.info("Generate map files")
        tools_dir = "various_small_datasets/tools"
        template_dir = tools_dir + "/map_templates"
        map_dir = tools_dir + "/map_files"
        if not os.path.exists(map_dir):
            os.mkdir(map_dir)
        env = Environment(loader=FileSystemLoader(template_dir))
        env.trim_blocks = True
        env.lstrip_blocks = True
        datasets = DataSet.objects.filter(enable_maplayer=True)
        for ds in datasets:
            log.info(f"Generate map file for {ds.name}")
            map_content = get_map_content(env, ds)
            mapfile_name = f"{map_dir}/{ds.name}.map"
            with open(mapfile_name, "w") as f:
                f.write(map_content)

        log.info(f"End generating mapfiles, results written to: {map_dir}")
