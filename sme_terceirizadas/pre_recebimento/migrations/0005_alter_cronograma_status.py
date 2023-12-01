# Generated by Django 3.2.16 on 2023-03-01 16:34

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0004_alter_cronograma_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cronograma",
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
                        "ASSINADO_FORNECEDOR",
                        "SOLICITADO_ALTERACAO",
                        "ASSINADO_CRONOGRAMA",
                        "ASSINADO_DINUTRE",
                        "ASSINADO_CODAE",
                    ],
                ),
            ),
        ),
    ]
