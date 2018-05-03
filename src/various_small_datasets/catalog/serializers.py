import logging
import math
from rest_framework.serializers import Serializer

log = logging.getLogger(__name__)


def _zoomlevel_for_scaledenom(scaledenom, domax=True):
    if scaledenom == 0:
        return 16  # max zoomlevel
    constant1 = 10400000  # TODO is this always correct ?? 
    zlf = math.log(constant1 / scaledenom, 2)
    if domax:
        zoomlevel = int(math.ceil(zlf))
    else:
        zoomlevel = int(math.floor(zlf))
    return 16 if zoomlevel >= 16 else 8 if zoomlevel <= 8 else zoomlevel


class MetaAPISerializer(Serializer):

    def to_representation(self, obj):
        result = {
            'name': obj.name,
        }
        if obj.description is not None and obj.description != '':
            result['description'] = obj.description
        if obj.enable_maplayer and len(obj.maplayer_set.all()) > 0:
            result['map_urlpath'] = f'/maps/{obj.name}?version=1.3.0&service=WMS'
            map_layers = []
            for layer in obj.maplayer_set.all():
                map_layers.append({
                    'id': f"{obj.name}{layer.id}",
                    'name': layer.name,
                    'title': layer.title,
                    'minzoom': _zoomlevel_for_scaledenom(layer.maxscale, False),
                    'maxzoom': _zoomlevel_for_scaledenom(layer.minscale, True),
                })
                result['map_layers'] = map_layers
        if obj.enable_api:
            result['api_url_path'] = f'/vsd/{obj.name}/'
        if obj.enable_geosearch:
            result['geosearch_url_path'] = f'/geosearch/{obj.name}/'
        return result

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


