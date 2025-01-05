from django import forms
from meldung.models import Fall


class StatistikForm(forms.Form):
    # Schritt 1: Auswahl der Hauptkategorie
    KATEGORIEN = [
        ('ort', 'Ort'),
        ('jahrgangsstufe', 'Jahrgangsstufe'),
        ('geschlecht', 'Geschlecht'),
        ('status', 'Status'),
    ]
    kategorie = forms.ChoiceField(
        choices=KATEGORIEN,
        label="Was möchtest du analysieren?",
        widget=forms.RadioSelect
    )

    # Schritt 2: Dynamische Filteroptionen
    ORT_CHOICES = [('', '---')] + list(Fall.ORT_CHOICES)
    GESCHLECHT_CHOICES = [('', '---')] + list(Fall.GESCHLECHT_CHOICES)
    STATUS_CHOICES = [('', '---')] + list(Fall.STATUS_CHOICES)

    jahrgangsstufe_min = forms.IntegerField(
        required=False,
        label="Minimale Jahrgangsstufe",
        widget=forms.NumberInput(attrs={'placeholder': 'z.B. 5'}),
    )
    jahrgangsstufe_max = forms.IntegerField(
        required=False,
        label="Maximale Jahrgangsstufe",
        widget=forms.NumberInput(attrs={'placeholder': 'z.B. 13'}),
    )
    geschlecht = forms.ChoiceField(
        choices=GESCHLECHT_CHOICES,
        required=False,
        label="Geschlecht"
    )
    ort = forms.ChoiceField(
        choices=ORT_CHOICES,
        required=False,
        label="Ort"
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label="Status"
    )

    # Schritt 3: Auswahl der Diagrammtypen
    DIAGRAMMTYPEN = [
        ('bar', 'Balkendiagramm'),
        ('pie', 'Kreisdiagramm'),
        ('line', 'Liniendiagramm'),
    ]
    diagrammtyp = forms.ChoiceField(
        choices=DIAGRAMMTYPEN,
        label="Wie sollen die Ergebnisse dargestellt werden?",
        widget=forms.RadioSelect
    )