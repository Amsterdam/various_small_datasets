from django.urls import path

from various_small_datasets.gen_api import views

urls = [
    path('<str:dataset>/<int:pk>/', views.GenericViewSet.as_view({'get': 'retrieve'})),
    path('<str:dataset>/', views.GenericViewSet.as_view({'get': 'list'})),
]

# TODO add view  to show all datasets