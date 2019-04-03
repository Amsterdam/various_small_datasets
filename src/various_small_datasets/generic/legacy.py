from various_small_datasets.generic.catalog import get_model_def, get_import_def, get_source_def
from various_small_datasets.generic.model import get_serial, get_pk, get_name_field, get_geo_field


def get_legacy_definition(dataset):
    model_def = get_model_def(dataset)
    import_def = get_import_def(dataset)
    source_def = get_source_def(dataset)

    return {
        "datasets": [
            {
                "name": source_def['dataset'],
                "description": source_def['description'],
                "table_name": import_def['target'],
                "ordering": get_serial(model_def).field_name,
                "pk_field": get_pk(model_def).field_name,
                "enable_api": True,
                "name_field": get_name_field(model_def).field_name,
                "geometry_field": get_geo_field(model_def).field_name,
                "geometry_type": get_geo_field(model_def).geo_type,
                "enable_geosearch": True,
                "enable_maplayer": True,
                "map_title": source_def['dataset'],
                "map_abstract": source_def['description'],
                "map_layers": [
                    {
                        "name": source_def['dataset'],
                        "title": source_def['dataset'].capitalize(),
                        "abstract": source_def['description'],
                        "color": "0 70 153",
                        "minscale": 10,
                        "maxscale": 400000,
                        "label": "title",
                        "label_minscale": 10,
                        "label_maxscale": 10000
                    }
                ]
            }
        ]
    }