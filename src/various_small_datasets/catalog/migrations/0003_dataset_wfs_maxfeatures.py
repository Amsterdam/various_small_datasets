# Generated by Django 2.1.7 on 2019-04-15 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_auto_20190410_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='wfs_maxfeatures',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
