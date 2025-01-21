# meldung/urls.py

from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('meldung/erstellen/', views.fall_erstellen_view, name='fall_erstellen'),
    path('qr/', lambda request: redirect('/meldung/erstellen/', permanent=True)),
    path('meldung/erfolgreich/<str:fall_id>/', views.fall_erfolgreich_view, name='fall_erfolgreich'),
    path('', views.landing_page_view, name='landing_page'),
]