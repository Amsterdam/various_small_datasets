from django.contrib.gis.db import models
from various_small_datasets.catalog.models import DataSet
from django.db import connection

# Use of dynamic Django model for generic rest API
#
# Here we define a dynamic model that is used in a generic Django Rest View en Serializer
# The data below can obtained from a metadata catalog in a database.
# Then the DATASET_CONFIG can be filled by reading this metadata catalog on startup,
# and we can add new datasets and have the corresponding API on the fly without any
# code changes.

# meta_attrs = {
#     'managed': False,
#     'db_table': 'biz_view',
#     'ordering': ['id'],
# }
#
# BIZMeta = type('Meta', (object, ), meta_attrs)
#
# biz_attrs = {
#     'id': models.IntegerField(primary_key=True),
#     'naam': models.CharField(unique=True, max_length=128, blank=True, null=True),
#     'biz_type': models.CharField(max_length=64, blank=True, null=True),
#     'heffingsgrondslag': models.CharField(max_length=128, blank=True, null=True),
#     'website': models.CharField(max_length=128, blank=True, null=True),
#     'heffing': models.IntegerField(blank=True, null=True),
#     'bijdrageplichtigen': models.IntegerField(blank=True, null=True),
#     'verordening': models.CharField(max_length=128, blank=True, null=True),
#     'geometrie': models.GeometryField(db_column='wkb_geometry', srid=28992, blank=True, null=True),
#     '__module__': 'various_small_datasets.gen_api.models',
#     'Meta': BIZMeta,
#     '__str__': lambda self: getattr(self, 'naam'),
#     '__doc__': 'Bedrijfs Investerings Zones',
# }
#
# BIZModel = type("BIZModel", (models.Model,), biz_attrs)

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
    'geometry': models.GeometryField,
    # TODO add missing types
}


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

        (real_schema, real_table) = (schema, table)
        # Is this a view ?
#         query = '''
# select table_schema, table_name
# from information_schema.view_table_usage where
# view_schema = %s and view_name = %s
#         '''
#         cursor.execute(query, [schema, table])
#         rows = cursor.fetchall()
#         if rows:
#             (real_schema, real_table) = rows[0]
#
        # Get constraints (pk and unique).
        # If this is a view we would like to use the underlying table
        # But currently we do not yet know how to map the columns in the view
        # to the columns in the table because they can be renamed using AS
        # We would have to parse the information.schema.views.view_definition
        # statement to find out. So this currently not work for views
        query = '''
SELECT
ccu.column_name, constraint_type
FROM information_schema.table_constraints tc
JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
WHERE  tc.table_schema = %s AND tc.table_name = %s
        '''
        cursor.execute(query, [real_schema, real_table])
        rows = cursor.fetchall()
        if rows:
            for (name, constraint) in rows:
                if name in d_fields:
                    if constraint.upper() == 'PRIMARY KEY':
                        d_fields[name]['primary_key'] = True
                        d_fields[name]['null'] = False
                        pk_field = name
                    elif constraint.upper() == 'UNIQUE':
                        d_fields[name]['unique'] = True
                        if name_field is None and d_fields[name]['data_type'] in {'character varying', 'text'}:
                            name_field = name

        # Get srid for geometry columns
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


def read_all_datasets():
    """
    Read all dataset configurations from the catalog and set the result DATASET_CONFIG
    This should called at the start of the application, for example in the toplevel urls
    """

    datasets = DataSet.objects.filter(enable_api=True)
    for ds in datasets:
        schema = 'public' if ds.schema is None else ds.schema
        postgres_metadata = read_postgres_metadata(schema, ds.table_name)
        ds.pk_field = ds.pk_field or ds.ordering or postgres_metadata['pk_field']
        ds.ordering = ds.ordering or postgres_metadata['pk_field']
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
            new_attrs[field_name] = _MAP_DS_TYPE[data_type](**dsf)

        model_name = ds.name.upper() + 'Model'
        new_model = type(model_name, (models.Model,), new_attrs)
        DATASET_CONFIG[ds.name] = new_model
