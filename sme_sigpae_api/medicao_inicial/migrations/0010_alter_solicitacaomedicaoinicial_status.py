# Generated by Django 3.2.16 on 2023-02-10 16:15

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("medicao_inicial", "0009_alter_solicitacaomedicaoinicial_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="solicitacaomedicaoinicial",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=39,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE",
                    name="SolicitacaoMedicaoInicialWorkflow",
                    states=[
                        "MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE",
                        "MEDICAO_ENVIADA_PELA_UE",
                        "MEDICAO_CORRECAO_SOLICITADA",
                        "MEDICAO_CORRIGIDA_PELA_UE",
                        "MEDICAO_APROVADA_PELA_DRE",
                        "MEDICAO_APROVADA_PELA_CODAE",
                        "MEDICAO_ENCERRADA_PELA_CODAE",
                    ],
                ),
            ),
        ),
    ]