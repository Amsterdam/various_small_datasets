import json
import logging

from rest_framework import serializers

from biz.dataset.models import BIZData
from various_small_datasets.api.rest import HALSerializer, DisplayField

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

class BIZSerializer(BaseSerializer, HALSerializer):

    _links = serializers.SerializerMethodField()
    _display = DisplayField()

    class Meta(object):
        model = BIZData
        fields = [
            '_links',
            '_display',
            'biz_id',
            'naam',
            'biz_type',
            'heffingsgrondslag',
            'website',
            'heffing',
            'bijdrageplichtigen',
            'verordening',
            'wkb_geometry'
        ]

    def get__links(self, obj):
        links = self.dict_with_self_href(
            '/biz/biz/{}/'.format(
                obj.biz_id))
        if obj.website != None:
            links["website"] = { "href": obj.website }
        if obj.verordening != None:
            verordening = obj.verordening.lstrip('#').rstrip('#')
            links["verordening"] = { "verordening": verordening }

        return links


