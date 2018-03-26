from django.urls import path

from various_small_datasets.gen_api import views
from various_small_datasets.gen_api.dataset_config import read_all_datasets

urls = [
    path('<str:dataset>/<int:pk>/', views.GenericViewSet.as_view({'get':'retrieve'})),
    path('<str:dataset>/', views.GenericViewSet.as_view({'get':'list'})),
]


# Initialize datasets from the catalog configuration
read_all_datasets()
