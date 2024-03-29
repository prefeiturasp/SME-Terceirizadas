# Generated by Django 2.2.13 on 2020-07-27 20:01

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0040_auto_20200720_1555"),
    ]

    operations = [
        migrations.AddField(
            model_name="reclamacaodeproduto",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=32,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="AGUARDANDO_AVALIACAO",
                    name="ReclamacaoProdutoWorkflow",
                    states=[
                        "AGUARDANDO_AVALIACAO",
                        "AGUARDANDO_RESPOSTA_TERCEIRIZADA",
                        "RESPONDIDO_TERCEIRIZADA",
                        "CODAE_ACEITOU",
                        "CODAE_RECUSOU",
                    ],
                ),
            ),
        ),
    ]
