from dataclasses import dataclass, asdict

#  Serializing with Jinja templates
from jinja2 import Environment, FileSystemLoader
import mappyfile

from . import types


def remove_none_values(items):
    print(items)
    return filter(
        lambda i: i[1] is not None,
        items
    )


def schema_dict(items):
    return dict(
        remove_none_values(items)
    )


@dataclass
class MappyfileSerializer:
    template: str = "MAP END"

    def map_file_to_dict(self, map_file):
        return asdict(map_file, dict_factory=schema_dict)
        return {
            '__type__': 'map',
            'name': map_file.name,
            'imagetype': 'png',
            'imagecolor': [-1, -1 ,-1],
            'web': {
                '__type__': 'web',
                'metadata': {
                    '__type__': 'metadata',
                    'ows_title': map_file.name,
                    'ows_srs': 'EPSG:3857 EPSG:4326 EPSG:900913',
                    'ows_enable_request': '*'
                }
            },
            'projection': ["init=epsg:4326"],
            'web': asdict(map_file.web),
            
            'layers': [
                asdict(layer, dict_factory=schema_dict)
                for layer in map_file.layers
            ]
        }

    def __call__(self, map_file: types.Mapfile):
        backend_file = mappyfile.loads(self.template)
        backend_file.update(self.map_file_to_dict(map_file))
        errors = mappyfile.validate(backend_file)
        if errors:
            raise Exception(errors)
        return mappyfile.dumps(backend_file)
    

@dataclass
class JinjaSerializer:
    template_dir: str

    @property
    def env(self) -> Environment:
        env = Environment(
            loader=FileSystemLoader(self.template_dir)
        )
        env.trim_blocks = True
        env.lstrip_blocks = True
        return env
    
    def __call__(self, template_file_name: str, context: dict):
        template = self.env.get_template(
            template_file_name
        )
        return template.render(**context)