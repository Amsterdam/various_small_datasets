from django.contrib.gis.db import models
# Use of dynamic Django model for generic rest API
#
# Here we define a dynamic model that is used in a generic Django Rest View en Serializer
# The data below can obtained from a metadata catalog in a database.
# Then the DATASET_CONFIG can be filled by reading this metadata catalog on startup,
# and we can add new datasets and have the corresponding API on the fly without any
# code changes.

meta_attrs = {
    'managed': False,
    'db_table': 'biz_data',
    'ordering': ['id'],
}

BIZMeta = type('Meta', (object, ), meta_attrs)

biz_attrs = {
    'id': models.IntegerField(db_column='biz_id', primary_key=True),
    'naam': models.CharField(unique=True, max_length=128, blank=True, null=True),
    'biz_type': models.CharField(max_length=64, blank=True, null=True),
    'heffingsgrondslag': models.CharField(max_length=128, blank=True, null=True),
    'website': models.CharField(max_length=128, blank=True, null=True),
    'heffing': models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
    'bijdrageplichtigen': models.IntegerField(blank=True, null=True),
    'verordening': models.CharField(max_length=128, blank=True, null=True),
    'geometrie': models.GeometryField(db_column='wkb_geometry', srid=28992, blank=True, null=True),
    '__module__': 'various_small_datasets.gen_api.models',
    'Meta': BIZMeta,
    '__str__': lambda self: getattr(self, 'naam'),
}

BIZModel = type("BIZModel", (models.Model,), biz_attrs)

DATASET_CONFIG = {
    'biz': BIZModel,
    'baz': BIZModel,
}
