import logging

from datapunt_api.serializers import HALSerializer, DisplayField
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from various_small_datasets.catalog.models import DataSet

log = logging.getLogger(__name__)


class BaseSerializer(object):

    def href_url(self, path):
        """Prepend scheme and hostname"""
        base_url = '{}://{}'.format(
            self.context['request'].scheme,
            self.context['request'].get_host())
        return base_url + path

    def dict_with_self_href(self, path):
        return {
            "self": {
                "href": self.href_url(path)
            }
        }

    def dict_with__links_self_href_id(self, path, id, id_name):
        return {
            "_links": {
                "self": {
                    "href": self.href_url(path.format(id))
                }
            },
            id_name: id
        }

    def dict_with_count_href(self, count, path):
        return {
            "count": count,
            "href": self.href_url(path)
        }


class GenericSerializer(BaseSerializer, HALSerializer):
    _links = serializers.SerializerMethodField()
    _display = DisplayField()

    class Meta(object):
        model = None
        fields = [
            '_links',
            '_display',
        ]

    def get__links(self, obj):
        links = self.dict_with_self_href(
            '/vsd/{}/{}/'.format(
                self.context['dataset'],
                obj.get_id()))
        return links


def get_fields(model):
    """
    This gets the fields for a model
    """
    return [x.name for x in model._meta.get_fields()]


def serializer_factory(dataset, model, as_geojson):
    """Generate the DRF serializer class for a specific dataset model."""
    if as_geojson:
        return geojson_serializer_factory(dataset, model)

    # Generate "Meta" attribute
    fields = ['_links', '_display']
    fields.extend(get_fields(model))
    new_meta_attrs = {'model': model, 'fields': fields}

    # Generate serializer class
    serializer_name = dataset.upper() + 'GenericSerializer'
    new_attrs = {
        '__module__': 'various_small_datasets.gen_api.serializers',
        'Meta': type('Meta', (object,), new_meta_attrs),
    }
    return type(serializer_name, (GenericSerializer,), new_attrs)


def geojson_serializer_factory(dataset: str, model):
    ds = DataSet.objects.get(name=dataset)
    geo_field = ds.geometry_field
    if not geo_field:
        raise RuntimeError("no geo information in model")

    serializer_name = dataset.upper() + 'GeoJSONSerializer'
    new_meta_attrs = {'model': model, 'fields': get_fields(model), 'geo_field': geo_field}
    new_meta = type('Meta', (object,), new_meta_attrs)
    new_attrs = {
        '__module__': 'various_small_datasets.gen_api.serializers',
        'Meta': new_meta,
    }

    return type(serializer_name, (GeoFeatureModelSerializer,), new_attrs)
