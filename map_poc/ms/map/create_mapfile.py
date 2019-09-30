from dataclasses import dataclass, asdict
import typing

import mappyfile


@dataclass
class Schema:
    name: str


def schema_to_mapfile(schema):
    return {
        '__type__': 'map',
        'name': schema.name,
        'imagetype': 'png',
        'imagecolor': [-1, -1 ,-1],
        'symbolset': 'symbolset.txt',
        'shapepath': '/map/',
        'web': {
            '__type__': 'web',
            'metadata': {
                '__type__': 'metadata',
                'ows_title': 'Airports',
                'ows_srs': 'EPSG:3857 EPSG:4326 EPSG:900913',
                'ows_enable_request': '*'
            }
        },
        'projection': ["init=epsg:4326"],
        
        'layers': [
            {
                '__type__': 'layer',
                'name': schema.name,
                'type': 'point',
                'connection': 'user=postgres password=insecure dbname=airports host=database',
                'connectiontype': 'postgis',
                'data': ['geom from ne_10m_airports'],
                'classes': [{
                    '__type__': 'class',
                    'styles': [{
                        '__type__': 'style',
                        'symbol': 'circlef',
                        'size': 10,
                        'width': 1,
                        'color': [255, 0, 0],
                        'outlinecolor': [0, 255, 0]
                    }]
                }]
           }
        ]
    }


class MapFileSerializer:
    template: str = "MAP END"

    def __call__(self, map_file: dict):
        backend_file = mappyfile.loads(self.template)
        backend_file.update(map_file)
        errors = mappyfile.validate(backend_file)
        if errors:
            raise Exception(errors)
        return mappyfile.dumps(backend_file)


class MapFileFactory:
    serializer: MapFileSerializer = MapFileSerializer()

    def __call__(self, schema: Schema):
        map_file = schema_to_mapfile(schema)
        return self.serializer(map_file)


@dataclass
class ApplicationContext:
    factory: MapFileFactory


@dataclass
class Application:
    context: ApplicationContext

    def create_map_file(self, schema):
        return self.context.factory(schema)


if __name__ == "__main__":
    app = Application(
        ApplicationContext(
            factory=MapFileFactory()
        )
    )
    map_file = app.create_map_file(
        Schema(
            name="airports"
        )
    )
    print(map_file)

"""
MAP
    NAME "test"
    LAYER
        NAME "test"
        DATA "select some_geo_field from table"
        TYPE POINT
    END
END
"""