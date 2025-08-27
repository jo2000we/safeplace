from django.db import migrations, models


def update_konfliktpartei_values(apps, schema_editor):
    Fall = apps.get_model('meldung', 'Fall')
    Fall.objects.filter(konfliktpartei='Schüler*innen').update(konfliktpartei='Schülerinnen und Schüler')
    Fall.objects.filter(konfliktpartei='Lehrer*innen').update(konfliktpartei='Lehrerinnen und Lehrer')


class Migration(migrations.Migration):

    dependencies = [
        ('meldung', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fall',
            name='konfliktpartei',
            field=models.CharField(
                max_length=30,
                choices=[
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
                ],
                verbose_name='Konfliktpartei',
            ),
        ),
        migrations.RunPython(update_konfliktpartei_values, migrations.RunPython.noop),
    ]

