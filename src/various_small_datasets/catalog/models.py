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

    def pk_field(self):
        pkfields = self.datasetfield_set.filter(primary_key=True)
        if len(pkfields) >= 1:  # In Django we only have one PK field
            return pkfields[0]
        else:
            return None

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
