# ZiehSafe/urls.py (Haupt-URL-Konfiguration)

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('meldung.urls')),
    path('', include('fallverwaltung.urls')),
]
