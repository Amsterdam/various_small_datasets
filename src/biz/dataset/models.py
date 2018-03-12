# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class BIZData(models.Model):
    id = models.IntegerField(db_column='biz_id', primary_key=True)
    naam = models.CharField(unique=True, max_length=128, blank=True, null=True)
    biz_type = models.CharField(max_length=64, blank=True, null=True)
    heffingsgrondslag = models.CharField(max_length=128, blank=True, null=True)
    website = models.CharField(max_length=128, blank=True, null=True)
    heffing = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bijdrageplichtigen = models.IntegerField(blank=True, null=True)
    verordening = models.CharField(max_length=128, blank=True, null=True)
    geometrie = models.GeometryField(db_column='wkb_geometry', srid=28992, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'biz_data'
        ordering = ['id']

    def __str__(self):
        if self.naam:
            return self.naam
        return "BIZ {}".format(self.id)