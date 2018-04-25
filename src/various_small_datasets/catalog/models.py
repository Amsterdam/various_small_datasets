from django.contrib.gis.db import models


class DataSet(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=30, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    database = models.CharField(max_length=128, null=True)  # default is 'default'
    schema = models.CharField(max_length=128, null=True)  # default is 'public'.
    # Schemas are not really supported in Django
    table_name = models.CharField(max_length=128, null=False)
    ordering = models.CharField(max_length=128, null=True)
    pk_field = models.CharField(max_length=128, null=True)
    enable_api = models.BooleanField()
    name_field = models.CharField(max_length=128, null=True)
    geometry_field = models.CharField(max_length=128, null=True)  # if null no geometry field
    geometry_type = models.CharField(max_length=32)  # POINT, POLYGON, LINE
    enable_geosearch = models.BooleanField()
    enable_maplayer = models.BooleanField()
    map_template = models.CharField(max_length=128, null=True)  # default = 'default'
    map_title = models.CharField(max_length=128, null=True)
    map_abstract = models.CharField(max_length=128, null=True)

    class Meta:
        managed = True
        db_table = 'cat_dataset'
        ordering = ['id']

    def __str__(self):
        return self.name


class MapLayer(models.Model):
    id = models.AutoField(primary_key=True)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False, null=False)
    title = models.CharField(max_length=128, blank=False, null=False)
    abstract = models.CharField(max_length=128, blank=False, null=True)
    filter = models.CharField(max_length=128, blank=False, null=True)
    color = models.CharField(max_length=11, null=True)  # RGB hex start with # last 2 digits translucence or 3 numbers
    style = models.TextField(null=True)
    minscale = models.PositiveIntegerField(null=True)
    maxscale = models. PositiveIntegerField(null=True)
    label = models.CharField(max_length=128, null=True)
    label_minscale = models.PositiveIntegerField(null=True)
    label_maxscale = models.PositiveIntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'cat_maplayer'
        ordering = ['id']

    def __str__(self):
        return self.name
