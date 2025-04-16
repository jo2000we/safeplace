from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
import os
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import StatistikForm
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TimeSlotForm, TimeSlotReassignmentForm
from .models import TimeSlot
from meldung.models import Fall

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Verzeichnisse
SPAM_MODEL_DIR = os.path.join(BASE_DIR, 'meldung/spam_model')
UPDATE_FILE = os.path.join(SPAM_MODEL_DIR, 'update.csv')


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
def update_fall_spam(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        kennung = data.get('kennung')
        status = data.get('status')

        try:
            fall = Fall.objects.get(kennung=kennung)
            fall.status = status
            fall.save()

            # Beschreibungs- und Status-Mapping für CSV
            description = fall.beschreibung
            label = 1 if status == 'offen' else 0

            # Protokollierung in CSV
            def log_update_to_csv(description, label):
                import pandas as pd

                # Prüfen, ob die Datei existiert
                if os.path.exists(UPDATE_FILE):
                    # Datei laden
                    df = pd.read_csv(UPDATE_FILE)

                    # Prüfen, ob die Beschreibung bereits existiert
                    if description in df['text'].values:
                        # Wert aktualisieren
                        df.loc[df['text'] == description, 'label'] = label
                    else:
                        # Neue Zeile hinzufügen
                        new_data = pd.DataFrame([{'text': description, 'label': label}])
                        df = pd.concat([df, new_data], ignore_index=True)
                else:
                    # Neue Datei erstellen, wenn sie nicht existiert
                    df = pd.DataFrame([{'text': description, 'label': label}])

                # CSV speichern
                df.to_csv(UPDATE_FILE, index=False)

            # Aufruf der Funktion
            log_update_to_csv(description, label)

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
def statistiken_view(request):
    form = StatistikForm()
    return render(request, 'statistiken.html', {'form': form})


@login_required
def statistiken_data(request):
    # Eingaben verarbeiten
    kategorie = request.GET.get('kategorie')
    print(f"Empfangene Parameter: {request.GET}")
    print(kategorie)
    diagrammtyp = request.GET.get('diagrammtyp')

    # Filter aus den GET-Parametern abrufen
    filters = {
        'jahrgangsstufe__gte': request.GET.get('jahrgangsstufe_min'),
        'jahrgangsstufe__lte': request.GET.get('jahrgangsstufe_max'),
        'geschlecht': request.GET.get('geschlecht'),
        'ort': request.GET.get('ort'),
        'status': request.GET.get('status'),
    }

    # Leere Filter entfernen
    filters = {k: v for k, v in filters.items() if v}  # Entfernt leere oder None-Werte

    # Validierung des ausgewählten Attributs
    if not kategorie or kategorie not in ['jahrgangsstufe', 'geschlecht', 'ort', 'status']:
        return JsonResponse({'error': 'Ungültige Kategorie ausgewählt.'}, status=400)

    # Daten abrufen und gruppieren
    try:
        daten = (
            Fall.objects.filter(**filters)
            .values(kategorie)  # Gruppiere nach der gewählten Kategorie
            .annotate(anzahl=Count('kennung'))  # Zähle Fälle pro Gruppe
            .order_by('-anzahl')  # Sortiere absteigend nach Anzahl
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse(list(daten), safe=False)


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


User = get_user_model()  # Damit greifen wir auf das Teacher-Modell zu, falls es als AUTH_USER_MODEL registriert ist.


@login_required
def appointment_dashboard(request):
    # Alte Zeitfenster löschen (Endzeit liegt vor dem aktuellen Zeitpunkt)
    TimeSlot.objects.filter(end_time__lt=timezone.now()).delete()
    teacher = request.user

    # Gespeicherte Zeitfenster des aktuellen Lehrers
    # Gebuchte Termine: mit zugeordnetem Fall (Termin mit gebuchtem Fall)
    my_booked_timeslots = TimeSlot.objects.filter(
        teacher=teacher,
        fall__isnull=False
    ).order_by('start_time')

    # Freie Zeitfenster des aktuellen Lehrers (die du im Abschnitt "Meine freien Zeitfenster" anzeigen möchtest)
    my_free_timeslots = TimeSlot.objects.filter(
        teacher=teacher,
        fall__isnull=True
    ).order_by('start_time')

    # Freie Zeitfenster von allen Lehrern, die in "Alle freien Zeitfenster" angezeigt werden
    free_timeslots = TimeSlot.objects.filter(
        fall__isnull=True,
        start_time__gte=timezone.now()
    ).order_by('start_time')

    # Liste aller Lehrer (ohne den eigenen Account) für den Reassign-Modal
    teacher_list = User.objects.exclude(id=teacher.id)

    context = {
        'my_booked_timeslots': my_booked_timeslots,
        'my_timeslots': my_free_timeslots,  # Im Template als "Meine freien Zeitfenster" anzeigen
        'free_timeslots': free_timeslots,
        'teacher_list': teacher_list,
        # Optional: Falls du auch Edit- oder Reassign-Formulare separat behandeln möchtest:
        'edit_form': None,
        'edit_timeslot': None,
        'reassign_form': None,
        'reassign_timeslot': None,
    }

    return render(request, 'appointment_dashboard.html', context)


@login_required
def edit_appointment(request, timeslot_id):
    teacher = request.user
    # Stelle sicher, dass der TimeSlot zum aktuellen Lehrer gehört
    timeslot = get_object_or_404(TimeSlot, id=timeslot_id, teacher=teacher)

    if request.method == 'POST':
        form = TimeSlotForm(request.POST, instance=timeslot)
        if form.is_valid():
            form.save()
            return redirect('appointment_dashboard')
    else:
        form = TimeSlotForm(instance=timeslot)

    # Holen aller relevanten Zeitfenster, damit alle Abschnitte auf dem Dashboard sichtbar bleiben.
    # Gebuchte Termine (für den Bereich "Meine Termine")
    my_booked_timeslots = TimeSlot.objects.filter(
        teacher=teacher,
        fall__isnull=False
    ).order_by('start_time')

    # Freie Zeitfenster des aktuellen Lehrers (für den Bereich "Meine freien Zeitfenster")
    my_free_timeslots = TimeSlot.objects.filter(
        teacher=teacher,
        fall__isnull=True
    ).order_by('start_time')

    # Freie Zeitfenster von allen Lehrern (für den Bereich "Alle freien Zeitfenster")
    free_timeslots = TimeSlot.objects.filter(
        fall__isnull=True,
        start_time__gte=timezone.now()
    ).order_by('start_time')

    # Liste aller Lehrer (ohne den aktuellen Lehrer) für den Reassign-Modal
    User = get_user_model()
    teacher_list = User.objects.exclude(id=teacher.id)

    context = {
        'my_booked_timeslots': my_booked_timeslots,
        'my_timeslots': my_free_timeslots,  # Wird im Template als "Meine freien Zeitfenster" angezeigt
        'free_timeslots': free_timeslots,
        'teacher_list': teacher_list,
        'edit_form': form,  # Wird zur Anzeige des Edit-Modals genutzt
        'edit_timeslot': timeslot,  # Damit das Modal weiß, um welchen Termin es geht
    }

    return render(request, 'appointment_dashboard.html', context)


@login_required
def reassign_appointment(request, timeslot_id):
    timeslot = get_object_or_404(TimeSlot, id=timeslot_id)
    if request.method == 'POST':
        form = TimeSlotReassignmentForm(request.POST)
        if form.is_valid():
            # neuen Lehrer setzen
            timeslot.teacher = form.cleaned_data['new_teacher']
            # Telefonnummer aus dem Formular mitnehmen, falls übergeben
            phone = form.cleaned_data.get('phone_number')
            if phone is not None:
                timeslot.phone_number = phone
            # beides speichern
            timeslot.save(update_fields=['teacher', 'phone_number'])
            return redirect('appointment_dashboard')
    else:
        form = TimeSlotReassignmentForm(initial={
            'new_teacher': timeslot.teacher.id,
            'phone_number': timeslot.phone_number,
        })

    # Falls noch ein GET‑Fallback nötig ist:
    teacher = request.user
    context = {
        'my_timeslots': TimeSlot.objects.filter(teacher=teacher).order_by('start_time'),
        'free_timeslots': TimeSlot.objects.filter(fall__isnull=True, start_time__gte=timezone.now()),
        'teacher_list': User.objects.exclude(id=teacher.id),
        'reassign_form': form,
        'reassign_timeslot': timeslot,
    }
    return render(request, 'appointment_dashboard.html', context)


@login_required
def create_appointment(request):
    if request.method == "POST":
        # Hole Daten aus dem Formular
        start_time_str = request.POST.get("start_time")
        duration_str = request.POST.get("duration", "15")
        phone_number = request.POST.get("phone_number")
        repeat = request.POST.get("repeat")  # Checkbox: Gibt 'on' zurück, wenn aktiviert
        repeat_end_date_str = request.POST.get("repeat_end_date") if repeat else None

        try:
            duration = int(duration_str)
        except ValueError:
            # Ungültiger Wert für Dauer
            return render(request, "appointment_dashboard.html", {
                "error": "Ungültiger Wert für die Dauer.",
            })

        # Parse den Startzeitpunkt
        try:
            # Der datetime-local Input liefert einen String im Format "YYYY-MM-DDThh:mm"
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        except Exception as e:
            return render(request, "appointment_dashboard.html", {
                "error": f"Ungültiges Datum/Zeitformat: {e}"
            })

        # Berechne Endzeit automatisch anhand der Dauer
        end_time = start_time + timedelta(minutes=duration)
        teacher = request.user

        # Falls keine Wiederholung gewünscht ist, erstellen wir ein einzelnes TimeSlot
        if not repeat or not repeat_end_date_str:
            TimeSlot.objects.create(
                teacher=teacher,
                start_time=start_time,
                end_time=end_time,
                phone_number=phone_number
            )
        else:
            # Wiederholung: parse das Wiederholungsende-Datum (Format: "YYYY-MM-DD")
            try:
                repeat_end_date = datetime.strptime(repeat_end_date_str, "%Y-%m-%d").date()
            except Exception as e:
                return render(request, "appointment_dashboard.html", {
                    "error": f"Ungültiges Wiederholungsende-Datum: {e}"
                })

            # Erstelle ein Zeitfenster für jede Woche ab dem Startzeitpunkt, solange das Datum noch <= repeat_end_date ist.
            current_start = start_time
            while current_start.date() <= repeat_end_date:
                current_end = current_start + timedelta(minutes=duration)
                TimeSlot.objects.create(
                    teacher=teacher,
                    start_time=current_start,
                    end_time=current_end,
                    phone_number=phone_number
                )
                current_start += timedelta(days=7)

        return redirect("appointment_dashboard")
    else:
        # Falls nicht POST, umleiten zur Dashboard-Seite
        return redirect("appointment_dashboard")


@login_required
def delete_appointment(request, timeslot_id):
    # Nur freie Zeitfenster, die dem aktuellen Lehrer gehören, löschen
    timeslot = get_object_or_404(TimeSlot, id=timeslot_id, teacher=request.user, fall__isnull=True)
    if request.method == 'POST':
        timeslot.delete()
        return redirect('appointment_dashboard')
    # Falls GET: Kann alternativ auch einen Fallback haben oder per AJAX genutzt werden
    return redirect('appointment_dashboard')


@login_required
@require_POST
def update_phone(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)
    slot.phone_number = request.POST.get("phone_number") or slot.phone_number
    slot.save(update_fields=["phone_number"])
    return redirect("appointment_dashboard")
