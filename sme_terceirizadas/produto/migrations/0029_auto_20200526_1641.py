# Generated by Django 2.2.10 on 2020-05-26 19:41

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0028_auto_20200514_1420"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homologacaodoproduto",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=32,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="HomologacaoProdutoWorkflow",
                    states=[
                        "RASCUNHO",
                        "CODAE_PENDENTE_HOMOLOGACAO",
                        "CODAE_HOMOLOGADO",
                        "CODAE_NAO_HOMOLOGADO",
                        "CODAE_QUESTIONADO",
                        "CODAE_PEDIU_ANALISE_SENSORIAL",
                        "TERCEIRIZADA_CANCELOU",
                        "HOMOLOGACAO_INATIVA",
                        "CODAE_SUSPENDEU",
                        "ESCOLA_OU_NUTRICIONISTA_RECLAMOU",
                        "CODAE_PEDIU_ANALISE_RECLAMACAO",
                        "CODAE_AUTORIZOU_RECLAMACAO",
                    ],
                ),
            ),
        ),
    ]
