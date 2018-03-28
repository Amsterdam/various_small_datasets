from django.contrib.gis.db import models
from django.forms.models import model_to_dict
from various_small_datasets.catalog.models import DataSet, DataSetField

# Use of dynamic Django model for generic rest API
#
# Here we define a dynamic model that is used in a generic Django Rest View en Serializer
# The data below can obtained from a metadata catalog in a database.
# Then the DATASET_CONFIG can be filled by reading this metadata catalog on startup,
# and we can add new datasets and have the corresponding API on the fly without any
# code changes.

# meta_attrs = {
#     'managed': False,
#     'db_table': 'biz_data',
#     'ordering': ['id'],
# }
#
# BIZMeta = type('Meta', (object, ), meta_attrs)
#
# biz_attrs = {
#     'id': models.IntegerField(db_column='biz_id', primary_key=True),
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
# }
#
# BIZModel = type("BIZModel", (models.Model,), biz_attrs)

DATASET_CONFIG = {
    # 'biz': BIZModel,
    # 'baz': BIZModel,
}

_MAP_DS_TYPE = {
    'char': models.CharField,
    'integer': models.IntegerField,
    'decimal': models.DecimalField,
    'datetime': models.DateTimeField,
    'geometry': models.GeometryField,
    # TODO add missing types
}


def read_all_datasets():
    """
    Read all dataset configurations from the catalog and set the result DATASET_CONFIG
    This should called at the start of the application, for example in the toplevel urls
    """
    datasets = DataSet.objects.filter(enable_api=True)
    for ds in datasets:
        new_meta_attrs = {'managed': False, 'db_table': ds.table_name, 'ordering': [ds.ordering]}
        new_meta = type('Meta', (object, ), new_meta_attrs)
        new_attrs = {
            '__module__': 'various_small_datasets.gen_api.models',
            '__str__': lambda self: getattr(self, ds.name_field),
            'Meta': new_meta,
        }

        for dataset_fields in ds.datasetfield_set.all():
            dsf = model_to_dict(dataset_fields, fields=['name', 'unique', 'primary_key', 'data_type', 'db_column',
                                                        'max_length', 'blank', 'null', 'max_digits', 'decimal_places',
                                                        'srid'])
            field_name = dsf.pop('name')
            data_type = dsf.pop('data_type')
            dsf_values = {k: v for k, v in dsf.items() if v is not None}
            # TODO add error checking
            new_attrs[field_name] = _MAP_DS_TYPE[data_type](**dsf_values)

        model_name = ds.name.upper() + 'Model'
        new_model = type(model_name, (models.Model,), new_attrs)
        DATASET_CONFIG[ds.name] = new_model
