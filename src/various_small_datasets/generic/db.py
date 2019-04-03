from django.db import connection

from various_small_datasets.generic.model import get_model_repr


def create_new_datatable(datatabel_name, model_def):
    new_datatable = f"{datatabel_name}_new"

    model_repr = get_model_repr(model_def)
    field_sql = [field.psql for field in model_repr]
    field_separator = " ,\n    "

    sql = f"""BEGIN;

DROP TABLE IF EXISTS {new_datatable};

CREATE TABLE {new_datatable} (
    {field_separator.join(field_sql)}
);

COMMIT;"""

    with connection.cursor() as cursor:
        cursor.execute(sql)


def roll_over_datatable(datatable_name, model_def):
    new_datatable = f"{datatable_name}_new"
    old_datatable = f"{datatable_name}_old"

    model_repr = get_model_repr(model_def)
    indices = "".join([field.psql_index(datatable_name) for field in model_repr])

    sql = f"""BEGIN;

ALTER TABLE IF EXISTS {datatable_name} RENAME TO {old_datatable};
ALTER TABLE {new_datatable} RENAME TO {datatable_name};

DROP TABLE IF EXISTS {old_datatable} CASCADE;

{indices}

COMMIT;"""

    with connection.cursor() as cursor:
        cursor.execute(sql)
