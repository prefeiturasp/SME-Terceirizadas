# Generated by Django 2.2.13 on 2022-09-02 15:03

import django.core.validators
from django.db import migrations, models


def tipo_turno_default(apps, _):
    PeriodoEscolar = apps.get_model("escola", "PeriodoEscolar")
    PeriodoEscolar.objects.filter(nome="MANHA").update(tipo_turno=1)
    PeriodoEscolar.objects.filter(nome="INTERMEDIARIO").update(tipo_turno=2)
    PeriodoEscolar.objects.filter(nome="TARDE").update(tipo_turno=3)
    PeriodoEscolar.objects.filter(nome="VESPERTINO").update(tipo_turno=4)
    PeriodoEscolar.objects.filter(nome="NOITE").update(tipo_turno=5)
    PeriodoEscolar.objects.filter(nome="INTEGRAL").update(tipo_turno=6)


def backwards(apps, _):
    PeriodoEscolar = apps.get_model("escola", "PeriodoEscolar")
    PeriodoEscolar.objects.update(tipo_turno=None)


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0052_auto_20220718_1810"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodoescolar",
            name="tipo_turno",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
        migrations.RunPython(tipo_turno_default, backwards),
    ]
