from django.urls import path, re_path 
# from core.admin import admin_site
from .views import *


app_name ="spectraModelling"


urlpatterns = [
    path('match/', match, name='match'),
    path('match_upload/', match_upload, name='upload'),
    # re_path('plot/', plot.as_view(), name='plot'),
    # path('admin/', admin_site.urls),
    # path('chartJSON/' , LineChartJSONView.as_view(), name='line_chart_json'),
    # path('chart/', line_chart, name='line_chart'),
    # re_path(r'chartJSON/(?:model=(?P<model>\w+))?\&(?:ids=(?P<ids>[0-9,]+))?', line_chart_json, name='line_chart_json'),
]