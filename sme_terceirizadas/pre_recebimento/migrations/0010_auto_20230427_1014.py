# Generated by Django 3.2.16 on 2023-04-27 10:14

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0009_alter_solicitacaoalteracaocronograma_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cronograma",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=32,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="CronogramaWorkflow",
                    states=[
                        "RASCUNHO",
                        "ASSINADO_E_ENVIADO_AO_FORNECEDOR",
                        "ALTERACAO_CODAE",
                        "ASSINADO_FORNECEDOR",
                        "SOLICITADO_ALTERACAO",
                        "ASSINADO_DINUTRE",
                        "ASSINADO_CODAE",
                    ],
                ),
            ),
        ),
        migrations.AlterField(
            model_name="solicitacaoalteracaocronograma",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=17,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="EM_ANALISE",
                    name="CronogramaAlteracaoWorkflow",
                    states=[
                        "EM_ANALISE",
                        "CRONOGRAMA_CIENTE",
                        "APROVADO_DINUTRE",
                        "REPROVADO_DINUTRE",
                        "APROVADO_DILOG",
                        "REPROVADO_DILOG",
                    ],
                ),
            ),
        ),
    ]
