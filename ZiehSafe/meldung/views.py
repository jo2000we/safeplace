from django.shortcuts import render, redirect, get_object_or_404
from .forms import FallForm
from .models import Fall
from flair.data import Sentence
from django.conf import settings
import torch
import os
from .services import get_tokenizer, get_model, get_tagger  # Services für Modell-Initialisierung und Wiederverwendung
import re

# Lade die Modelle über einen zentralisierten Service
tokenizer = get_tokenizer()
model = get_model()
tagger = get_tagger()


# Funktion zum Testen des Modells
def test_spam(text):
    try:
        # Tokenisiere den Text
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            # Führe eine Vorhersage durch
            outputs = model(**inputs)
            logits = outputs.logits
            # Bestimme das vorhergesagte Label
            predicted_class = torch.argmax(logits, dim=1).item()  # 1 für echte Fälle, 0 für Spam
        return predicted_class
    except Exception as e:
        # Logging hinzufügen
        print(f"Fehler bei der Spam-Prüfung: {e}")
        return 0  # Standardmäßig als Spam behandeln


def anonymisiere_beschreibung(text):
    try:
        sentence = Sentence(text)
        tagger.predict(sentence)

        anonymized_text = text
        for entity in sentence.get_spans('ner'):
            entity_type = entity.get_label("ner").value
            placeholder = {
                "PER": "[PERSON]",
                "LOC": "[ORT]",
                "ORG": "[ORGANISATION]",
                "MISC": "[VERSCHIEDENES]",
            }.get(entity_type, "[ANONYMISIERT]")

            # Sichere Ersetzung mit Wortgrenzen
            anonymized_text = re.sub(r'\b' + re.escape(entity.text) + r'\b', placeholder, anonymized_text)

        return anonymized_text
    except Exception as e:
        print(f"Fehler bei der Anonymisierung: {e}")
        return "[FEHLER BEI DER ANONYMISIERUNG]"


def count_words(text):
    return len(text.split())


def fall_erstellen_view(request):
    if request.method == 'POST':
        form = FallForm(request.POST)
        if form.is_valid():
            fall = form.save(commit=False)  # Speichert das Objekt, aber noch nicht in der Datenbank

            # Wortbegrenzung prüfen
            max_words = 500
            word_count = count_words(fall.beschreibung)
            if word_count > max_words:
                form.add_error('beschreibung',
                               f'Die Beschreibung darf maximal {max_words} Wörter enthalten. Du hast {word_count} Wörter geschrieben.')
                return render(request, 'meldung/fall_formular.html', {'form': form})

            # Anonymisiere die Beschreibung
            fall.beschreibung = anonymisiere_beschreibung(fall.beschreibung)

            # Prüfe, ob die Meldung Spam ist
            if test_spam(fall.beschreibung) == 0:
                fall.status = 'abgelehnt'

            fall.save()  # Speichert den Fall in der Datenbank
            return redirect('fall_erfolgreich', fall_id=fall.kennung)
        else:
            # Fehleranzeige
            return render(request, 'meldung/fall_formular.html', {
                'form': form,
                'error_message': 'Das Formular enthält Fehler. Bitte überprüfen Sie Ihre Eingaben.'
            })
    else:
        form = FallForm()
    return render(request, 'meldung/fall_formular.html', {'form': form})


def fall_erfolgreich_view(request, fall_id):
    fall = get_object_or_404(Fall, kennung=fall_id)
    return render(request, 'meldung/fall_erfolgreich.html', {'fall_id': fall_id})


def landing_page_view(request):
    return render(request, 'landing_page.html')
