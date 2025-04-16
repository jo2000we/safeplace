from django.conf import settings
from meldung.models import Fall
from django.contrib.auth.models import AbstractUser
from django.db import models


class Teacher(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Männlich'),
        ('W', 'Weiblich'),
        ('D', 'Divers'),
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name="Geschlecht"
    )

    class Meta:
        verbose_name = "Lehrer"
        verbose_name_plural = "Lehrer"

    def __str__(self):
        return self.username


class TimeSlot(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_slots',
        verbose_name="Beratungslehrer"
    )
    start_time = models.DateTimeField(verbose_name="Startzeit")
    end_time = models.DateTimeField(verbose_name="Endzeit")
    fall = models.ForeignKey(
        Fall,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_slots',
        verbose_name="Zugeordneter Fall"
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name="Telefonnummer",
        help_text="Gib hier die Telefonnummer ein, die den Schülern angezeigt wird."
    )

    class Meta:
        ordering = ['start_time']
        verbose_name = "Verfügbarkeitsfenster"
        verbose_name_plural = "Verfügbarkeitsfenster"

    def __str__(self):
        if self.fall:
            fall_info = f" | Fall: {self.fall.kennung}"
        else:
            fall_info = " (frei)"
        return f"{self.teacher.username}: {self.start_time.strftime('%d.%m.%Y %H:%M')} - {self.end_time.strftime('%d.%m.%Y %H:%M')}{fall_info}"
