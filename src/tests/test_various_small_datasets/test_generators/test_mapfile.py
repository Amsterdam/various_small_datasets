from various_small_datasets.generators.mapfile import (
    MapfileGenerator, AmsterdamSchema
)


def test_normal_generator():
    def serializer(mapfile):
        assert mapfile.name == "test"

    generator = MapfileGenerator(
        map_dir="bla/",
        serializer=serializer,
        datasets=[
            AmsterdamSchema({
                "id": "test",
                "services": {
                    "mapservice": {

                    }
                }
            })
        ]
    )
    generator.write = lambda n, fp: ""
    generator()
