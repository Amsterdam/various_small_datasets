from datapunt_api.rest import DatapuntViewSet
from various_small_datasets.catalog.serializers import MetaAPISerializer
from various_small_datasets.catalog.models import DataSet


class MetaAPIViewSet(DatapuntViewSet):
    queryset = DataSet.objects.all()
    serializer_detail_class = serializer_class = MetaAPISerializer