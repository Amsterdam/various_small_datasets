import logging
from django.contrib.gis.geos import Point
from rest_framework.exceptions import NotFound, ParseError

import various_small_datasets.gen_api.rest
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework import serializers as rest_serializers

from various_small_datasets.gen_api import serializers

import various_small_datasets.gen_api.dataset_config as config


log = logging.getLogger(__name__)


def valid_rd(x, y):

    rd_x_min = 100000
    rd_y_min = 450000
    rd_x_max = 150000
    rd_y_max = 500000

    if not rd_x_min <= x <= rd_x_max:
        return False

    if not rd_y_min <= y <= rd_y_max:
        return False

    return True


def valid_lat_lon(lat, lon):

    lat_min = 52.03560
    lat_max = 52.48769
    lon_min = 4.58565
    lon_max = 5.31360

    if not lat_min <= lat <= lat_max:
        return False

    if not lon_min <= lon <= lon_max:
        return False

    return True


def convert_input_to_float(value):

    err = None

    try:
        x, y = value.split(',')
    except ValueError:
        return None, None, f"Not enough values x, y {value}"

    # Converting to float
    try:
        x = float(x)
        y = float(y)
    except ValueError:
        return None, None, f"Invalid value {x} {y}"

    return x, y, err


def validate_x_y(value):
    """
    Check if we get valid values
    """
    point = None

    x, y, err = convert_input_to_float(value)

    if err:
        return None, None, err

    # Checking if the given coords are valid

    if valid_rd(x, y):
        point = Point(x, y, srid=28992)
    elif valid_lat_lon(x, y):
        point = Point(y, x, srid=4326).transform(28992, clone=True)
    else:
        err = "Coordinates received not within Amsterdam"

    return point, err


class GenericFilter(FilterSet):
    id = filters.CharFilter(method="id_filter")
    location = filters.CharFilter(method="location_filter")
    name = filters.CharFilter(method="name_filter")

    class Meta(object):
        model = None
        fields = (
            'naam',
            'locatie',
            'id',
        )

    @staticmethod
    def locatie_filter(queryset, _filter_name, value):
        """
        Filter based on the geolocation. This filter actually
        expect 2 numerical values: x and y
        The value given is broken up by ',' and converted
        to the value tuple
        """

        point, err = validate_x_y(value)

        if err:
            log.exception(err)
            raise rest_serializers.ValidationError(err)

        # Creating one big queryset
        biz_results = queryset.filter(
            geometrie__contains=point)
        return biz_results

    @staticmethod
    def naam_filter(queryset, _filter_name, value):
        return queryset.filter(
            naam__icontains=value
        )

    @staticmethod
    def id_filter(queryset, _filter_name, value):
        return queryset.filter(
            id__iexact=value
        )


def get_fields(model):
    """
    This gets the fields
    """
    return map(lambda x: x.name, model._meta.get_fields())


class GenericViewSet(various_small_datasets.gen_api.rest.DatapuntViewSet):
    """
    Generic Viewset for arbitrary Django models

    """
    initialized = False
    serializerClasses = {}

    def __init__(self, *args, **kwargs):
        self.dataset = None
        self.model = None
        # TODO add filtering
        # filter_class = GenericFilter
        self.filter_class = None
        super(GenericViewSet, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if not GenericViewSet.initialized:
            # Initialize datasets from the catalog configuration
            config.read_all_datasets()
            GenericViewSet.initialized = True

        if 'dataset' in self.kwargs:
            self.dataset = self.kwargs['dataset']
        else:
            raise ParseError("missing dataset")

        if self.dataset in config.DATASET_CONFIG:
            self.model = config.DATASET_CONFIG[self.dataset]
        else:
            raise NotFound("dataset" + self.dataset)

        GenericFilter.Meta.model = self.model()

        # TODO cache this in a dictionary per dataset, see if  it improves performance
        return self.model.objects.all()

    def get_serializer_class(self):
        if self.dataset not in GenericViewSet.serializerClasses:
            model_name = self.dataset.upper() + 'GenericSerializer'
            serializer_class = type(model_name, (serializers.GenericSerializer,), {})
            serializer_class.Meta.model = self.model
            serializer_class.Meta.fields.extend(get_fields(self.model))
            GenericViewSet.serializerClasses[self.dataset] = serializer_class
        return GenericViewSet.serializerClasses[self.dataset]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'dataset': self.dataset})
        return context
