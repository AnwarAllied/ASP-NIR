from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    path('', include('spectraModelling.urls')),
    # path('pages/', include('django.contrib.flatpages.urls')),
    # path('djadmin/', admin.site.urls),
]
