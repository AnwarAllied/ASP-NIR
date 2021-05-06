from django.urls import path 
from core.admin import admin_site
from .views import *


urlpatterns = [
    path('pca/', pca.as_view(), name='pca'),
    path('pca/save/', pca_save, name='pca_save'),
    path('pca/test/', pca_test.as_view(), name='pca_test'),
    path('chart-sc/', ScartterChartView.as_view(), name='scartter_chart_json'),
    path('pca_match/', pca_match, name='match'),
    path('match_upload/', pca_match_upload, name='pca_upload'),
    # path('pca/test/?model=<str:model>&ids=<str:ids>', pca_test.as_view(), name='pca_test'),
    path('pls/', pls.as_view(), name='pls'),
    path('pls/save/', pls_save, name='pls_save'),
    path('pls/test/', pls_test.as_view(), name='pls_test'),
    path('chart-pls/', PlsScatterChartView.as_view(), name='pls_chart_json'),
]
