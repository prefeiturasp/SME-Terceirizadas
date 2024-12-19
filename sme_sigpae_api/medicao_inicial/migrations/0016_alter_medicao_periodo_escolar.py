# Generated by Django 3.2.16 on 2023-03-21 13:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0056_logatualizadadosaluno"),
        ("medicao_inicial", "0015_altera_nome_grupo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="medicao",
            name="periodo_escolar",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="escola.periodoescolar",
            ),
        ),
    ]