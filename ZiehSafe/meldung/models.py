from django.db import models, IntegrityError

# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


def validate_char_count(value):
    max_chars = 5000
    if len(value) > max_chars:
        raise ValidationError(
            f"Die Beschreibung darf maximal {max_chars} Zeichen enthalten. ({len(value)} Zeichen aktuell)")


class Fall(models.Model):
    kennung = models.CharField(max_length=100, primary_key=True)
    jahrgangsstufe = models.IntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(13)],
        verbose_name="Jahrgangsstufe"
    )
    GESCHLECHT_CHOICES = [
        ('M', 'Männlich'),
        ('W', 'Weiblich'),
        ('D', 'Divers'),
    ]
    geschlecht = models.CharField(
        max_length=1,
        choices=GESCHLECHT_CHOICES,
        verbose_name="Geschlecht"
    )

    zeitpunkt_erstellung = models.DateTimeField(auto_now_add=True, verbose_name="Zeitpunkt der Meldung")
    zeitpunkt_vorfall = models.DateTimeField(null=True, blank=True, verbose_name="Zeitpunkt des Vorfalls")

    ORT_CHOICES = [
        ('Toilette', 'Toilette'),
        ('Klassenraum', 'Klassenraum'),
        ('Flur', 'Flur'),
        ('Pausenhof', 'Pausenhof'),
        ('Schulweg', 'Schulweg'),
        ('Online', 'Online (WhatsApp, Instagram, Schul.Cloud...)'),
        ('Woanders', 'Woanders'),
    ]

    ort = models.CharField(
        max_length=20,
        choices=ORT_CHOICES,
        verbose_name="Ort"
    )

    KONFLIKTPARTEI_CHOICES = [
        ('Schüler', 'Schüler (eine Person, Männlich)'),
        ('Schülerin', 'Schülerin (eine Person, Weiblich)'),
        ('Divers', 'eine Person (Divers)'),
        ('Schülerinnen und Schüler', 'Schülerinnen und Schüler (Mehrzahl)'),
        ('Lehrer', 'ein Lehrer (Männlich)'),
        ('Lehrerin', 'eine Lehrerin (weiblich)'),
        ('Lehrerinnen und Lehrer', 'Lehrerinnen und Lehrer (Mehrzahl)'),
        ('Eltern', 'Eltern'),
        ('Schulpersonal', 'Schulpersonal'),
        ('Andere', 'Andere'),
    ]

    konfliktpartei = models.CharField(
        max_length=30,
        choices=KONFLIKTPARTEI_CHOICES,
        verbose_name="Konfliktpartei"
    )

    STATUS_CHOICES = [
        ('positiv_geschlossen', 'Positiv geschlossen'),
        ('negativ_geschlossen', 'Negativ geschlossen'),
        ('offen', 'Offen'),
        ('abgelehnt', 'Abgelehnt'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offen',  # Standardwert setzen
        verbose_name="Status"
    )

    beschreibung = models.TextField(
        verbose_name="Beschreibung",
        validators=[validate_char_count]
    )

    def save(self, *args, **kwargs):
        # Setzt den Vorfallszeitpunkt auf den Erstellungszeitpunkt, falls dieser nicht gesetzt ist
        if not self.zeitpunkt_vorfall:
            self.zeitpunkt_vorfall = self.zeitpunkt_erstellung
        # Generiert eine eindeutige Kennung, falls noch nicht vorhanden
        if not self.kennung:
            for _ in range(1000):  # Versuch, eine eindeutige Kennung zu generieren (max. Versuche)
                self.kennung = str(uuid.uuid4()).replace('-', '')[:10]  # Kürzt auf 10 Zeichen
                try:
                    super().save(*args, **kwargs)
                    break  # Erfolgreiches Speichern -> Schleife beenden
                except IntegrityError:
                    self.kennung = None  # Bei Konflikt erneut generieren
            else:
                raise ValueError("Es konnte keine eindeutige Kennung generiert werden.")

        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Jahrgangsstufe: {self.jahrgangsstufe}, Geschlecht: {self.get_geschlecht_display()}, \
                 Zeitpunkt der Erstellung: {self.zeitpunkt_erstellung}, Zeitpunkt des Vorfalls: {self.zeitpunkt_vorfall}, \
                 Ort: {self.ort}, Konfliktpartei: {self.konfliktpartei}, Status: {self.get_status_display()}, \
                 Beschreibung: {self.beschreibung}"
