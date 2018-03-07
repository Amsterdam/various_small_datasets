import logging
from django.contrib.gis.geos import Point
from biz.dataset.models import BIZData
import various_small_datasets.api.rest
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters
from rest_framework import serializers as rest_serializers

from biz.api import serializers

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

    x = None
    y = None
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
    x = None
    y = None
    err = None
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
        err = "Coordinates recieved not within Amsterdam"

    return point, err


class BIZFilter(FilterSet):
    id = filters.CharFilter()

    locatie = filters.CharFilter(method="locatie_filter")

    # verblijfs object filter

    class Meta(object):
        model = BIZData
        fields = (
            'id',
            'naam',
            'locatie'
        )

    def locatie_filter(self, queryset, _filter_name, value):
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
            wkb_geometry__dcontains=(point))
        return biz_results


class BIZViewSet(various_small_datasets.api.rest.DatapuntViewSet):
    serializer_detail_class = serializers.BIZSerializer

    queryset = BIZData.objects.all()
    filter_class = BIZFilter

    def get_serializer_class(self):
        return serializers.BIZSerializer