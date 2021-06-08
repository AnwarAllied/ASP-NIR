from django.urls import path, re_path 
# from core.admin import admin_site
from masterModelling.views import master_pca_chart
from .views import *


app_name ="spectraModelling"


urlpatterns = [
    path('match/', match, name='match'),
    path('match_upload/', match_upload, name='upload'),
    path('match/<int:id>/method/<int:method_id>', match_method.as_view(), name='method'),
    path('match/<int:match_id>/chart', master_pca_chart.as_view(), name='chart'),
    # path('get_match_upload/',get_match_upload)
]