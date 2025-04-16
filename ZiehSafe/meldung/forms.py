from django import forms
from .models import Fall


class FallForm(forms.ModelForm):
    class Meta:
        model = Fall
        fields = ['jahrgangsstufe', 'geschlecht', 'zeitpunkt_vorfall', 'ort', 'konfliktpartei', 'beschreibung']
        widgets = {
            'jahrgangsstufe': forms.Select(choices=[(i, str(i)) for i in range(5, 14)]),
            'beschreibung': forms.Textarea(attrs={'maxlength': 4000}),
        }