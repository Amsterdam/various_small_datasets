from rest_framework import routers

from biz.api import views as api_views


class BIZView(routers.APIRootView):
    """
    De bedrijfsinvesteringszones in de stad worden hier als een lijst getoond.

    """


class BIZRouter(routers.DefaultRouter):
    APIRootView = BIZView


biz = BIZRouter()
biz.register(r'biz', api_views.BIZViewSet, base_name='biz')
urls = biz.urls
