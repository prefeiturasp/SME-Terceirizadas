# Generated by Django 2.2.13 on 2022-11-08 21:27

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0061_auto_20221026_1156"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fluxocronograma",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=21,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="CronogramaWorkflow",
                    states=[
                        "RASCUNHO",
                        "ENVIADO_AO_FORNECEDOR",
                        "ALTERACAO_CODAE",
                        "APROVADO",
                        "REPROVADO",
                        "ALTERACAO_FORNECEDOR",
                        "VALIDADO_FORNECEDOR",
                    ],
                ),
            ),
        ),
    ]
