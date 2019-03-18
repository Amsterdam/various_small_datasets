import logging

from datapunt_api.serializers import HALSerializer, DisplayField
from rest_framework import serializers

from various_small_datasets.geojson import geojson_api

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
    return map(lambda x: x.name, model._meta.get_fields())


def serializer_factory(dataset, model):
    if dataset in geojson_api.datasets:
        return geojson_api.get_serializer(dataset)

    model_name = dataset.upper() + 'GenericSerializer'
    fields = ['_links', '_display']
    fields.extend(get_fields(model))
    new_meta_attrs = {'model': model, 'fields': fields}
    new_meta = type('Meta', (object,), new_meta_attrs)
    new_attrs = {
        '__module__': 'various_small_datasets.gen_api.serializers',
        'Meta': new_meta,
    }
    return type(model_name, (GenericSerializer,), new_attrs)
