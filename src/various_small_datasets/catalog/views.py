from datapunt_api.rest import DatapuntViewSet
from various_small_datasets.catalog.serializers import MetaAPISerializer
from various_small_datasets.catalog.models import DataSet


class MetaAPIViewSet(DatapuntViewSet):
    queryset = DataSet.objects.all()
    serializer_detail_class = serializer_class = MetaAPISerializer
    filter_fields = ('enable_api', 'enable_maplayer', 'enable_geosearch')

    def get_queryset(self):
        """
        Optionally restricts the returned datasets to given name(s),
        by filtering against a `name` query parameter in the URL.
        """
        queryset = DataSet.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            names = name.split(",")
            queryset = queryset.filter(name__in=names)
        return queryset
