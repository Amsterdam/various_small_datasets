import json
import logging

from django.contrib.gis.measure import D
from django_filters.rest_framework import filters, FilterSet
from rest_framework import serializers as rest_serializers

from various_small_datasets.geojson.geojson_db import geojson_model_factory
from various_small_datasets.gen_api import serializers
from various_small_datasets.gen_api import views

log = logging.getLogger(__name__)

with open("various_small_datasets/geojson/geojson_datasets.json") as json_file:
    datasets_config = json.load(json_file)
    datasets = [item['dataset'] for item in datasets_config]


def get_model(dataset):
    return geojson_model_factory(dataset)


def get_filter(dataset):
    class GeoJSONGenericFilter(FilterSet):
        location = filters.CharFilter(field_name='geometry', method="location_filter")

        class Meta(object):
            model = geojson_model_factory(dataset)
            fields = ('location',)

        @staticmethod
        def location_filter(queryset, _, value):
            point, radius, err = views.validate_x_y(value)

            if err:
                log.exception(err)
                raise rest_serializers.ValidationError(err)

            if radius is not None:
                return queryset.filter(geometry__distance_lte=(point, D(m=radius)))

            return queryset.filter(geometry__contains=point)

    return GeoJSONGenericFilter


def get_serializer(dataset):
    class GeoJSONGenericSerializer(serializers.GenericSerializer):
        class Meta(object):
            model = geojson_model_factory(dataset)
            fields = ['_links', '_display', 'id', 'geometry', 'properties']

    return GeoJSONGenericSerializer
