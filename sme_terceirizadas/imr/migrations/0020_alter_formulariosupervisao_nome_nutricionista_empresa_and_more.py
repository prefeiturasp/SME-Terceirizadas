# Generated by Django 4.2.7 on 2024-05-10 11:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("imr", "0019_remove_formulariosupervisao_apresentou_ocorrencias"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formulariosupervisao",
            name="nome_nutricionista_empresa",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="Nome da Nutricionista RT da Empresa",
            ),
        ),
        migrations.AlterField(
            model_name="formulariosupervisao",
            name="periodo_visita",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="formularios_supervisao",
                to="imr.periodovisita",
                verbose_name="Período da Visita",
            ),
        ),
    ]