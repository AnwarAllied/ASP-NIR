from django.urls import path

from core.admin import admin_site
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('plot/', views.plot, name='plot'),
    path('admin/', admin_site.urls),
]