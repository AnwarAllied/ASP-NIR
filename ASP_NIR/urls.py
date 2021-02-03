from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    path('', include('spectraModelling.urls')),
    path('', include('predictionModel.urls')),
    # path('404/', permission_denied_view),
    # path('pages/', include('django.contrib.flatpages.urls')),
    # path('djadmin/', admin.site.urls),
]

handler404 = 'core.views.error_404'