from django.urls import path
from core.admin import admin_site
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('get_spc/<int:spc_id>', get_spc),
    path('get_pro/<int:spc_id>', get_pro),
    path('get_own/', get_own),
    path('xlsx/', download_xlsx, name='xlsx'),
    path('plot/', plot.as_view(), name='plot'),
    path('admin/', admin_site.urls),
    path('chartJSON/' , LineChartJSONView.as_view(), name='line_chart_json'),
    path('chartResl', LineChartResl.as_view(), name='line_chart_resl'),
    # path('chart/', line_chart, name='line_chart'),
    # re_path(r'chartJSON/(?:model=(?P<model>\w+))?\&(?:ids=(?P<ids>[0-9,]+))?', line_chart_json, name='line_chart_json'),
    path('upload_auto/', upload_auto)
]
