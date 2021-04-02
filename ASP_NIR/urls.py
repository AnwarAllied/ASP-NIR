from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django.views.static import serve
from ASP_NIR.settings import MEDIA_ROOT

urlpatterns = [
    path('', include('core.urls')),
    path('', include('spectraModelling.urls')),
    path('', include('predictionModel.urls')),
    path('preprocessing', include('preprocessingFilters.urls')),
    # path('404/', permission_denied_view),
    # path('pages/', include('django.contrib.flatpages.urls')),
    # path('djadmin/', admin.site.urls),
    url(r'^media/(?P<path>.*)$', serve, {"document_root":MEDIA_ROOT})
]

handler404 = 'core.views.error_404'