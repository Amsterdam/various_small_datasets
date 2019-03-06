import logging
import re
import time

from datapunt_api.rest import DatapuntViewSet
from rest_framework.exceptions import NotFound, ParseError

from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework import serializers as rest_serializers, viewsets
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from rest_framework.generics import ListCreateAPIView

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


def get_location_args(args):
    if 'lat' in args or 'lon' in args or 'x' in args or 'y' in args:
        lat = args.get('lat', None)
        lon = args.get('lon', None)
        x = args.get('x', None)
        y = args.get('y', None)
        radius = args.get('radius', 0)
        if lat and lon:
            x = lon
            y = lat
            rd = False
        elif x and y:
            rd = True
        else:
            raise rest_serializers.ValidationError("missing lat/lon or x/y arguments")

        try:
            x = float(x)
            y = float(y)
            radius = int(radius)
        except ValueError:
            raise rest_serializers.ValidationError("invalid lat/lon or x/y or radius arguments")

        point = Point(x, y, srid=28992) if rd else Point(x, y, srid=4326).transform(28992, clone=True)
        return point, radius

    else:
        return None, None


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


def filter_factory(ds_name, model, ds):
    model_name = ds_name.upper() + 'GenericFilter'
    name_field = ds.name_field or 'UNKNOWN'
    geometry_field = ds.geometry_field or 'UNKNOWN'
    geometry_type = ds.geometry_type or 'UNKNOWN'
    fields = [name_field, geometry_field]
    location_filter_name = ':'.join([geometry_field, geometry_type])
    location = filters.CharFilter(field_name=location_filter_name, method="location_filter")
    name = filters.CharFilter(field_name=name_field, method="name_filter")

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


class BaseGenericViewSet():
    """
    Base Generic Viewset for arbitrary Django models

    """
    INITIALIZE_DELAY = 600  # 10 minutes
    initialized = 0

    def __init__(self, *args, **kwargs):
        self.dataset_name = None
        self.dataset = None
        self.model = None
        self.filter_class = None
        super(BaseGenericViewSet, self).__init__(*args, **kwargs)

    def _filter_geosearch(self, queryset):
        geometry_field = self.dataset.geometry_field or None
        geometry_type = self.dataset.geometry_type or None

        if geometry_field and geometry_type:
            point, radius = get_location_args(self.request.query_params)
            if point:
                if geometry_type.lower() == 'polygon':
                    args = {'__'.join([geometry_field, 'contains']): point}
                    queryset = queryset.filter(**args)
                elif geometry_type.lower() == 'point' and radius is not None:
                    args = {'__'.join([geometry_field, 'dwithin']): (point, D(m=radius))}
                    queryset = queryset.filter(**args).annotate(distance=Distance(geometry_field, point))
                else:
                    err = "Radius in argument expected"
                    raise rest_serializers.ValidationError(err)

        return queryset

    @classmethod
    def initialize(cls):
        if time.time() - BaseGenericViewSet.initialized > cls.INITIALIZE_DELAY:
            config.read_all_datasets()
            BaseGenericViewSet.initialized = time.time()

    def get_queryset(self):
        if 'dataset' in self.kwargs:
            self.dataset_name = self.kwargs['dataset']
        else:
            raise ParseError("missing dataset")

        if self.dataset_name in config.DATASET_CONFIG:
            self.model = config.DATASET_CONFIG[self.dataset_name]
        else:
            BaseGenericViewSet.initialize()
            if self.dataset_name in config.DATASET_CONFIG:
                self.model = config.DATASET_CONFIG[self.dataset_name]
            else:
                raise NotFound("dataset" + self.dataset_name)

        return self.model.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'dataset': self.dataset_name})
        detail = True if 'detail' not in self.request.query_params or self.request.query_params[
            'detail'] == '1' else False
        context.update({'detail': detail})
        return context

    @classmethod
    def get_all_datasets(cls):
        BaseGenericViewSet.initialize()
        datasets = {}
        for k, v in config.DATASET_CONFIG.items():
            datasets[k] = v.__doc__
        return datasets


class GenericViewSet(BaseGenericViewSet, DatapuntViewSet):
    serializerClasses = {}
    filterClasses = {}
    dataSetsClasses = {}

    def get_serializer_class(self):
        if self.dataset_name not in type(self).serializerClasses:
            type(self).serializerClasses[self.dataset_name] = \
                serializers.serializer_factory(self.dataset_name, self.model)
        serializer = type(self).serializerClasses[self.dataset_name]
        return serializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == 'list':
            if self.dataset_name not in type(self).dataSetsClasses:
                type(self).dataSetsClasses[self.dataset_name] = DataSet.objects.get(name=self.dataset_name)
                type(self).filterClasses[self.dataset_name] = \
                    filter_factory(self.dataset_name, self.model, type(self).dataSetsClasses[self.dataset_name])
            self.filter_class = type(self).filterClasses[self.dataset_name]
            self.dataset = type(self).dataSetsClasses[self.dataset_name]

        return queryset


class GeoGenericViewSet(BaseGenericViewSet, ListCreateAPIView):
    serializerClasses = {}
    filterClasses = {}
    dataSetsClasses = {}

    def get_serializer_class(self):
        if self.dataset_name not in type(self).serializerClasses:
            type(self).serializerClasses[self.dataset_name] = serializers.geosearch_serializer_factory(
                self.dataset_name, self.model,
                self.dataset.pk_field,
                self.dataset.geometry_field)
        serializer = type(self).serializerClasses[self.dataset_name]
        return serializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.dataset_name not in type(self).dataSetsClasses:
            type(self).dataSetsClasses[self.dataset_name] = DataSet.objects.get(name=self.dataset_name)
        self.dataset = type(self).dataSetsClasses[self.dataset_name]

        if self.dataset.enable_geosearch:
            queryset = self._filter_geosearch(queryset)

        return queryset
