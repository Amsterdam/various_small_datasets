from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.fields import JSONField
from django.db import models

geojson_models = {}


def create_new_datatable_sql(dataset_name):
    new_datatable = f"{dataset_name}_new"

    return f"""BEGIN;

DROP TABLE IF EXISTS {new_datatable};

CREATE TABLE {new_datatable} (
    {dataset_name}_id SERIAL,
    id varchar(256),
    geometry geometry(geometry, 4326),
    properties jsonb
);

COMMIT;"""


def roll_over_datatable_sql(dataset_name):
    new_datatable = f"{dataset_name}_new"
    old_datatable = f"{dataset_name}_old"

    return f"""BEGIN;

ALTER TABLE IF EXISTS {dataset_name} RENAME TO {old_datatable};
ALTER TABLE {new_datatable} RENAME TO {dataset_name};

DROP TABLE IF EXISTS {old_datatable};

CREATE UNIQUE INDEX {dataset_name}_idx ON {dataset_name} ({dataset_name}_id);
CREATE INDEX {dataset_name}_gix ON {dataset_name} USING GIST (geometry);

COMMIT;"""


def geojson_model_factory(dataset_name, new_table=False):
    global geojson_models

    table_name = f'{dataset_name}_new' if new_table else dataset_name

    if table_name not in geojson_models:
        class GeoJSONModel(models.Model):
            f"""{dataset_name}"""
            id = models.CharField(primary_key=True, max_length=256)
            geometry = GeometryField(srid=4326)
            properties = JSONField()

            class Meta:
                managed = False
                ordering = ['id']
                db_table = f'{table_name}'

            def get_id(self):
                return self.id

            def __str__(self):
                return f"<{dataset_name} | {self.id}>"

        geojson_models[table_name] = GeoJSONModel

    return geojson_models[table_name]
