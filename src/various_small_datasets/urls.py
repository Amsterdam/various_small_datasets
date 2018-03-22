from django.conf import settings
from django.urls import include, path
from rest_framework import response, schemas
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import CoreJSONRenderer
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework_swagger.renderers import SwaggerUIRenderer

from biz.api import urls as biz_urls
from various_small_datasets.gen_api import urls as gen_urls
from various_small_datasets.health import urls as health_urls

grouped_url_patterns = {
    'base_patterns': [
        path('status/', include(health_urls)),
    ],
    'biz_patterns': [
        path('vsd/biz/', include(biz_urls.urls)),
    ],
    'gen_patterns': [
        path('vsd/', include(gen_urls.urls)),
    ],
}

@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer, CoreJSONRenderer])
def biz_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='BedrijfsInvesteringsZones',
        patterns=grouped_url_patterns['biz_patterns']
    )
    return response.Response(generator.get_schema(request=request))


urlpatterns = [path('vsd/docs/api-docs/biz/',
                   biz_schema_view),
               ] + [url for pattern_list in grouped_url_patterns.values()
                    for url in pattern_list]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        path('__debug__/', include(debug_toolbar.urls)),
    ])