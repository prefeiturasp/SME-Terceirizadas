# Generated by Django 3.2.16 on 2023-02-19 01:28

import django_xworkflows.models
from django.db import migrations


def atualiza_status(apps, _):
    Cronograma = apps.get_model("pre_recebimento", "Cronograma")
    Cronograma.objects.filter(status="VALIDADO_FORNECEDOR").update(
        status="ASSINADO_FORNECEDOR"
    )


def backwards(apps, _):
    Cronograma = apps.get_model("pre_recebimento", "Cronograma")
    cronogramas = Cronograma.objects.filter(status="ASSINADO_FORNECEDOR")
    cronogramas.update(status="VALIDADO_FORNECEDOR")


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0003_alter_cronograma_status"),
    ]

    operations = [
        migrations.RunPython(atualiza_status, backwards),
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
                    ],
                ),
            ),
        ),
    ]
