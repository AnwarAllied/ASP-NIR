from django.urls import path
from core.admin import admin_site
from .views import *

urlpatterns = [
    path('master_static_pca/',master_pca.as_view(), name='masterpca'),
    path('master_static_pls/',master_pls.as_view(), name='masterpls'),
    path('master_pls_chart/',master_pls_chart.as_view(), name='masterplschart'),
]
