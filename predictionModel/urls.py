from django.urls import path 
from core.admin import admin_site
from .views import *

urlpatterns = [
    path('pca/', pca.as_view(), name='pca'),
    path('pls/', pls.as_view(), name='pls'),
    path('chart-sc/' , ScartterChartView.as_view(), name='scartter_chart_json'),
]
