import logging
from rest_framework.exceptions import NotFound, ParseError

import various_small_datasets.gen_api.rest
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework import serializers as rest_serializers
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from various_small_datasets.catalog.models import DataSet
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

    lvalues = value.split(',')
    if len(lvalues) < 2:
        return None, None, None, f"Not enough values x, y {value}"

    x = lvalues[0]
    y = lvalues[1]
    radius = lvalues[2] if len(lvalues) > 2 else None

    # Converting to float
    try:
        x = float(x)
        y = float(y)
        radius = None if radius is None else int(radius)
    except ValueError:
        return None, None, None, f"Invalid value {x} {y} {radius}"

    # checking sane radius size
    if radius is not None and radius > 1000:
        return None, None, None, "radius too big"

    return x, y, radius, err


def validate_x_y(value):
    """
    Check if we get valid values
    """
    point = None

    x, y, radius, err = convert_input_to_float(value)

    if err:
        return None, None, None, err

    # Checking if the given coords are valid

    if valid_rd(x, y):
        point = Point(x, y, srid=28992)
    elif valid_lat_lon(x, y):
        point = Point(y, x, srid=4326).transform(28992, clone=True)
    else:
        err = "Coordinates received not within Amsterdam"

    return point, radius, err


class GenericFilter(FilterSet):

    class Meta(object):
        model = None
        fields = ()

    @staticmethod
    def location_filter(queryset, _filter_name, value):
        """
        Filter based on the geolocation. This filter actually
        expect 2 or 3 numerical values: x, y and optional radius
        The value given is broken up by ',' and converted
        to the value tuple
        """

        point, radius, err = validate_x_y(value)

        if err:
            log.exception(err)
            raise rest_serializers.ValidationError(err)

        # Creating one big queryset
        (geo_field, geo_type) = _filter_name.split(':')

        if geo_type.lower() == 'polygon' and radius is None:
            args = {'__'.join([geo_field, 'contains']): point}
            biz_results = queryset.filter(**args)
        elif radius is not None:
            args = {'__'.join([geo_field, 'dwithin']): (point, D(m=radius))}
            biz_results = queryset.filter(**args).annotate(afstand=Distance(geo_field, point))
        else:
            err = "Radius in argument expected"
            log.exception(err)
            raise rest_serializers.ValidationError(err)
        return biz_results

    @staticmethod
    def name_filter(queryset, _filter_name, value):
        args = {'__'.join([_filter_name, 'icontains']): value}
        return queryset.filter(**args)


def filter_factory(ds_name, model):
    model_name = ds_name.upper() + 'GenericFilter'
    ds = DataSet.objects.get(name=ds_name)
    name_field = ds.name_field
    geometry_field = ds.geometry_field
    fields = model._meta.get_fields()
    for field in fields:
        if field.db_column == geometry_field:
            geometry_field = field.name
        if field.db_column == name_field:
            name_field = field.name
    geometry_type = ds.geometry_type
    fields = [name_field, geometry_field]
    location_filter_name = ':'.join([geometry_field, geometry_type])
    location = filters.CharFilter(name=location_filter_name, method="location_filter")
    name = filters.CharFilter(name=name_field, method="name_filter")

    new_meta_attrs = {'model': model,
                      'fields': fields,
                      }
    new_meta = type('Meta', (object,), new_meta_attrs)
    new_attrs = {
        '__module__': 'various_small_datasets.gen_api.filters',
        'Meta': new_meta,
        geometry_field: location,
        name_field: name,
    }
    return type(model_name, (GenericFilter,), new_attrs)


class GenericViewSet(various_small_datasets.gen_api.rest.DatapuntViewSet):
    """
    Generic Viewset for arbitrary Django models

    """
    initialized = False
    serializerClasses = {}
    filterClasses = {}

    def __init__(self, *args, **kwargs):
        self.dataset = None
        self.model = None
        # TODO add filtering
        # filter_class = GenericFilter
        self.filter_class = None
        super(GenericViewSet, self).__init__(*args, **kwargs)

    @classmethod
    def initialize(cls):
        if not GenericViewSet.initialized:
            config.read_all_datasets()
            GenericViewSet.initialized = True

    def get_queryset(self):
        GenericViewSet.initialize()

        if 'dataset' in self.kwargs:
            self.dataset = self.kwargs['dataset']
        else:
            raise ParseError("missing dataset")

        if self.dataset in config.DATASET_CONFIG:
            self.model = config.DATASET_CONFIG[self.dataset]
        else:
            raise NotFound("dataset" + self.dataset)

        if self.action == 'list':
            if self.dataset not in GenericViewSet.filterClasses:
                GenericViewSet.filterClasses[self.dataset] = filter_factory(self.dataset, self.model)
            self.filter_class = GenericViewSet.filterClasses[self.dataset]
        return self.model.objects.all()

    def get_serializer_class(self):
        if self.dataset not in GenericViewSet.serializerClasses:
            GenericViewSet.serializerClasses[self.dataset] = serializers.serializer_factory(self.dataset, self.model)
        return GenericViewSet.serializerClasses[self.dataset]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'dataset': self.dataset})
        return context

    @classmethod
    def get_all_datasets(cls):
        GenericViewSet.initialize()
        datasets = {}
        for k, v in config.DATASET_CONFIG.items():
            datasets[k] = v.__doc__
        return datasets