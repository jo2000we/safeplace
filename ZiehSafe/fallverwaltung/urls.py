# meldung/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('fallverwaltung/fall_uebersicht/', views.fall_uebersicht, name='fall_uebersicht'),
    path('login/', views.benutzer_login, name='benutzer_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/login/', views.benutzer_login, name='accounts_login'),  # Alias für Login
    path('fallverwaltung/abgeschlossene_faelle/', views.abgeschlossene_faelle, name='abgeschlossene_faelle'),
    path('statistiken/', views.statistiken, name='statistiken'),
    path('fall/update_status/', views.update_fall_status, name='update_fall_status'),
]
