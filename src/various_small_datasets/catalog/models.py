from django.contrib.gis.db import models


class DataSet(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=10, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    database = models.CharField(max_length=128, null=True)  # default is 'default'
    schema = models.CharField(max_length=128, null=True)  # default is 'public'.
    # Schemas are not really supported in Django
    table_name = models.CharField(max_length=128, null=False)
    ordering = models.CharField(max_length=128, null=True)
    enable_api = models.BooleanField()
    name_field = models.CharField(max_length=128, null=True)
    geometry_field = models.CharField(max_length=128, null=True)  # if null no geometry field
    geometry_type = models.CharField(max_length=32)  # POINT, POLYGON, LINE
    enable_geosearch = models.BooleanField()
    enable_maplayer = models.BooleanField()
    maplayer_template = models.CharField(max_length=128, null=True)  # default = 'default'
    maplayer_color = models.CharField(max_length=9, null=True)  # RGB hex start with # last 2 digits translucence
    maplayer_minscale = models.PositiveIntegerField(null=True)
    maplayer_maxscale = models. PositiveIntegerField(null=True)
    maplayer_label = models.CharField(max_length=128, null=True)
    maplayer_label_minscale = models.PositiveIntegerField(null=True)
    maplayer_lable_maxscale = models.PositiveIntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'cat_dataset'
        ordering = ['id']

    def __str__(self):
        return self.name


class DataSetField(models.Model):
    id = models.AutoField(primary_key=True)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False, null=False)
    data_type = models.CharField(max_length=128, blank=False, null=False)
    db_column = models.CharField(max_length=128, blank=False, null=True)  # Default same as name
    primary_key = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    max_length = models.PositiveSmallIntegerField(null=True)
    blank = models.BooleanField(default=False)
    null = models.BooleanField(default=False)
    max_digits = models.PositiveSmallIntegerField(null=True)
    decimal_places = models.PositiveSmallIntegerField(null=True)
    srid = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'cat_dataset_fields'
        ordering = ['id']
        unique_together = ('dataset', 'name',)

    def __str__(self):
        return self.name
