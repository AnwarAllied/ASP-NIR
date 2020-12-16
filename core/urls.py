from django.urls import path

from core.admin import admin_site
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('plot/', plot.as_view(), name='plot'),
    path('admin/', admin_site.urls),
    path('chart/', line_chart, name='line_chart'),
    path('chartJSON/', line_chart_json, name='line_chart_json'),
]