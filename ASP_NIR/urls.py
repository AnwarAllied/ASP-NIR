from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),
    path('', include('spectraModelling.urls')),
    # path('pages/', include('django.contrib.flatpages.urls')),
    # path('djadmin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
