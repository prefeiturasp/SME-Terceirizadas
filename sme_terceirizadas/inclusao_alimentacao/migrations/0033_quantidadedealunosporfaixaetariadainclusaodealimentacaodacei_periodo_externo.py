# Generated by Django 3.2.16 on 2023-02-21 04:29

import django.db.models.deletion
from django.db import migrations, models


def migracao_dados(apps, _):
    nome_modelo = "QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI"
    modelo = apps.get_model("inclusao_alimentacao", nome_modelo)
    for inclusao_cei in modelo.objects.all():
        inclusao_cei.periodo_externo = inclusao_cei.periodo
        inclusao_cei.save()


def backwards(apps, _):
    nome_modelo = "QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI"
    modelo = apps.get_model("inclusao_alimentacao", nome_modelo)
    for inclusao_cei in modelo.objects.all():
        inclusao_cei.periodo_externo = None
        inclusao_cei.save()


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0056_logatualizadadosaluno"),
        ("inclusao_alimentacao", "0032_auto_20230120_1711"),
    ]

    operations = [
        migrations.AddField(
            model_name="quantidadedealunosporfaixaetariadainclusaodealimentacaodacei",
            name="periodo_externo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="periodo_externo",
                to="escola.periodoescolar",
            ),
        ),
        migrations.RunPython(migracao_dados, backwards),
    ]
