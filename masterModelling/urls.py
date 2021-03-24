from django.urls import path
from core.admin import admin_site
from .views import *

urlpatterns = [
    path('master_static_pca/',master_pca.as_view(), name='masterpca'),
    # path('master_static_pls/',master_pls.as_view(), name='masterpls'),
    path('master_pca_chart/', master_pca_chart.as_view(), name='master_pca_chart'),
    # path('master_pca_element_chart/', master_pls_element_chart.as_view(), name='master_pca_element'),
    # path('master_pls_chart/',master_pls_chart.as_view(), name='master_pls_chart'),
    # path('master_pls_element_chart/',master_pls_element_chart.as_view(), name='master_pls_element'),
]
