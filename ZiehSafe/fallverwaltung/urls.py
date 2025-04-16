# meldung/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('fallverwaltung/fall_uebersicht/', views.fall_uebersicht, name='fall_uebersicht'),
    path('login/', views.benutzer_login, name='benutzer_login'),
    path('logout/', LogoutView.as_view(next_page='/accounts/login/?next=/fallverwaltung/fall_uebersicht/'), name='logout'),
    path('accounts/login/', views.benutzer_login, name='accounts_login'),  # Alias für Login
    path('fallverwaltung/abgeschlossene_faelle/', views.abgeschlossene_faelle, name='abgeschlossene_faelle'),
    path('statistiken/', views.statistiken_view, name='statistiken'),
    path('statistiken/data/', views.statistiken_data, name='statistiken_data'),
    path('fall/update_status/', views.update_fall_status, name='update_fall_status'),
    path('fall/update_spam/', views.update_fall_spam, name='update_fall_spam'),
    path('appointment-dashboard/', views.appointment_dashboard, name='appointment_dashboard'),
    path('appointment/create/', views.create_appointment, name='create_appointment'),
    path('appointment/edit/<int:timeslot_id>/', views.edit_appointment, name='edit_appointment'),
    path('appointment/reassign/<int:timeslot_id>/', views.reassign_appointment, name='reassign_appointment'),
    path('appointment/delete_appointment/<int:timeslot_id>/', views.delete_appointment, name='delete_appointment'),
]
