import logging
from django.contrib.gis.db import models
from various_small_datasets.catalog.models import DataSet
from django.db import connection

from various_small_datasets.generic import catalog
from various_small_datasets.generic.model import get_django_model_by_name

DATASET_CONFIG = {
    # 'biz': BIZModel,
    # 'baz': BIZModel,
}

_MAP_DS_TYPE = {
    'character varying': models.CharField,
    'char': models.CharField,
    'text': models.TextField,
    'integer': models.IntegerField,
    'decimal': models.DecimalField,
    'numeric': models.DecimalField,
    'datetime': models.DateTimeField,
    'date': models.DateField,
    'time without time zone': models.TimeField,
    'geometry': models.GeometryField,
    'polygon': models.PolygonField,
    'multipolygon': models.MultiPolygonField,
    'point': models.PointField,
    'timestamp with time zone': models.DateTimeField,
    'timestamp': models.DateTimeField,
    'real': models.FloatField,
    'double precision': models.FloatField,
    # TODO add missing types
}

log = logging.getLogger(__name__)


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def read_postgres_metadata(schema, table):  # noqa: C901
    pk_field = None
    name_field = None
    geometry_field = None

    with connection.cursor() as cursor:
        query = '''
SELECT column_name, data_type, character_maximum_length, is_nullable, numeric_precision, numeric_scale
FROM information_schema.columns
WHERE table_schema = %s AND table_name = %s
        '''
        cursor.execute(query, [schema, table])
        fields = dictfetchall(cursor)

        d_fields = {}
        for field in fields:
            name = field.pop('column_name')
            max_length = field.pop('character_maximum_length')
            if max_length is not None:
                field['max_length'] = max_length
            # numeric_precision and numeric_scale should always be popped from field, but only used if numeric
            max_digits = field.pop('numeric_precision')
            decimal_places = field.pop('numeric_scale')
            if field['data_type'] == 'numeric':
                field['max_digits'] = max_digits
                field['decimal_places'] = decimal_places

            field['null'] = field.pop('is_nullable') == 'YES'
            d_fields[name] = field

        query = '''
SELECT f_geometry_column, srid, type
FROM geometry_columns
WHERE f_table_schema = %s AND f_table_name = %s
        '''
        cursor.execute(query, [schema, table])
        rows = cursor.fetchall()
        if rows:
            for (geometry_field, srid, type1) in rows:
                if geometry_field in d_fields:
                    d_fields[geometry_field]['srid'] = srid
                    if d_fields[geometry_field]['data_type'] == 'USER-DEFINED':
                        d_fields[geometry_field]['data_type'] = type1.lower()

        return {'fields': d_fields,
                'pk_field': pk_field,
                'name_field': name_field,
                'geometry_field': geometry_field
                }


def read_all_datasets():  # noqa: C901
    """
    Read all dataset configurations from the catalog and set the result DATASET_CONFIG
    This should called at the start of the application, for example in the toplevel urls
    """

    datasets = DataSet.objects.filter(enable_api=True)
    for ds in datasets:
        if ds.name in DATASET_CONFIG:
            continue
        if ds.name in catalog.generic_importable:
            DATASET_CONFIG[ds.name] = get_django_model_by_name(ds.name)
            continue

        try:
            schema = 'public' if ds.schema is None else ds.schema
            postgres_metadata = read_postgres_metadata(schema, ds.table_name)
            ds.pk_field = ds.pk_field or ds.ordering or postgres_metadata['pk_field']
            ds.ordering = ds.ordering or ds.pk_field or postgres_metadata['pk_field']
            ds.name_field = ds.name_field or postgres_metadata['name_field']
            ds.geometry_field = ds.geometry_field or postgres_metadata['geometry_field']

            new_meta_attrs = {'managed': False, 'db_table': ds.table_name, 'ordering': [ds.ordering]}
            new_meta = type('Meta', (object, ), new_meta_attrs)
            new_attrs = {
                '__module__': 'various_small_datasets.gen_api.models',
                '__str__': lambda self, name_field=ds.name_field: getattr(self, name_field),
                'get_id': lambda self, pk_field=ds.pk_field: getattr(self, pk_field),
                'Meta': new_meta,
                '__doc__': ds.description,
            }

            dataset_fields = postgres_metadata['fields']
            for field_name, dsf in dataset_fields.items():
                data_type = dsf.pop('data_type')
                # Use pk definition in catalog to set primary_key
                # If this can be retrieved from Postgres this is not required
                if field_name == ds.pk_field:
                    dsf['primary_key'] = True
                    dsf['null'] = False
                new_attrs[field_name] = _MAP_DS_TYPE[data_type](**dsf)
        except KeyError as err:
            log.error(f'Error: Skip dataset for {ds.table_name} : {err}')
            continue

        model_name = ds.name.upper() + 'Model'
        new_model = type(model_name, (models.Model,), new_attrs)
        DATASET_CONFIG[ds.name] = new_model
