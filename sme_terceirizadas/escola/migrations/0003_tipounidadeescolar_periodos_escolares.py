# Generated by Django 2.2.6 on 2019-12-05 21:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0002_auto_20191205_1815"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipounidadeescolar",
            name="periodos_escolares",
            field=models.ManyToManyField(
                blank=True,
                related_name="tipos_unidade_escolar",
                to="escola.PeriodoEscolar",
            ),
        ),
    ]
