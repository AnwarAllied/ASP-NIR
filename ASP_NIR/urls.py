from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    # path('djadmin/', admin.site.urls),
]
