from django.contrib.auth.decorators import login_required
from meldung.models import Fall
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse


@login_required
def update_fall_status(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        kennung = data.get('kennung')
        status = data.get('status')

        try:
            fall = Fall.objects.get(kennung=kennung)
            fall.status = status
            fall.save()
            return JsonResponse({'success': True})
        except Fall.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Fall nicht gefunden'})

    return JsonResponse({'success': False, 'error': 'Ungültige Anfrage'})


@login_required
def fall_uebersicht(request):
    suchbegriff = request.GET.get('search', '')
    geschlecht_filter = request.GET.get('geschlecht', 'alle')
    ort_filter = request.GET.get('ort', 'alle')
    konfliktpartei_filter = request.GET.get('konfliktpartei', 'alle')

    # Alle Fälle holen
    alle_faelle = Fall.objects.all()

    # Wenn Suchbegriff angegeben wurde, Fälle entsprechend filtern
    if suchbegriff:
        alle_faelle = alle_faelle.filter(
            Q(kennung__icontains=suchbegriff) |
            Q(beschreibung__icontains=suchbegriff)
        )

    # Geschlechtsfilter anwenden, wenn ein spezielles Geschlecht gewählt wurde
    if geschlecht_filter and geschlecht_filter != 'alle':
        alle_faelle = alle_faelle.filter(geschlecht=geschlecht_filter)

    # Ortsfilter anwenden
    if ort_filter and ort_filter != 'alle':
        alle_faelle = alle_faelle.filter(ort=ort_filter)

    # Konfliktpartei-Filter anwenden
    if konfliktpartei_filter and konfliktpartei_filter != 'alle':
        alle_faelle = alle_faelle.filter(konfliktpartei=konfliktpartei_filter)

    # Normale Fälle (offen), die nicht abgelehnt sind
    faelle = alle_faelle.exclude(status='abgelehnt').filter(status='offen')

    # Spam-Fälle separat auswählen
    spam_faelle = alle_faelle.filter(status='abgelehnt')

    return render(request, 'fall_uebersicht.html', {
        'faelle': faelle,
        'spam_faelle': spam_faelle,
        'suchbegriff': suchbegriff,
        'geschlecht_filter': geschlecht_filter,
        'ort_filter': ort_filter,
        'konfliktpartei_filter': konfliktpartei_filter
    })


@login_required
def abgeschlossene_faelle(request):
    suchbegriff = request.GET.get('search', '')
    geschlecht_filter = request.GET.get('geschlecht', 'alle')

    # Alle abgeschlossenen Fälle holen (positiv oder negativ abgeschlossen)
    abgeschlossene_faelle = Fall.objects.filter(status__in=['positiv_geschlossen', 'negativ_geschlossen'])

    # Wenn Suchbegriff angegeben wurde, abgeschlossene Fälle entsprechend filtern
    if suchbegriff:
        abgeschlossene_faelle = abgeschlossene_faelle.filter(
            Q(kennung__icontains=suchbegriff) |
            Q(beschreibung__icontains=suchbegriff)
        )

    # Geschlechtsfilter anwenden, wenn ein spezielles Geschlecht gewählt wurde
    if geschlecht_filter and geschlecht_filter != 'alle':
        abgeschlossene_faelle = abgeschlossene_faelle.filter(geschlecht=geschlecht_filter)

    return render(request, 'abgeschlossene_faelle.html', {
        'faelle': abgeschlossene_faelle,
        'suchbegriff': suchbegriff,
        'geschlecht_filter': geschlecht_filter
    })


@login_required
def statistiken(request):
    return render(request, 'statistiken.html')


def benutzer_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('fall_uebersicht')  # Nach erfolgreichem Login zur Übersicht
        else:
            # Fehlernachricht bei falschen Anmeldedaten
            return render(request, 'login.html', {'error': 'Ungültiger Benutzername oder Passwort'})

    return render(request, 'login.html')


def benutzer_logout(request):
    logout(request)
    return redirect('/login/')
