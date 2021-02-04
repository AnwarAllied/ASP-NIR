from django.urls import path
from core.admin import admin_site
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('plot/', plot.as_view(), name='plot'),
    path('admin/', admin_site.urls),
    path('chartJSON/' , LineChartJSONView.as_view(), name='line_chart_json'),
    # path('chart/', line_chart, name='line_chart'),
    # re_path(r'chartJSON/(?:model=(?P<model>\w+))?\&(?:ids=(?P<ids>[0-9,]+))?', line_chart_json, name='line_chart_json'),
]
