# Generated by Django 2.2.13 on 2021-10-20 14:14

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("logistica", "0042_auto_20211019_1431"),
    ]

    operations = [
        migrations.AlterField(
            model_name="guia",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=31,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="AGUARDANDO_ENVIO",
                    name="GuiaRemessaWorkFlow",
                    states=[
                        "AGUARDANDO_ENVIO",
                        "AGUARDANDO_CONFIRMACAO",
                        "PENDENTE_DE_CONFERENCIA",
                        "DISTRIBUIDOR_REGISTRA_INSUCESSO",
                        "RECEBIDA",
                        "NAO_RECEBIDA",
                        "RECEBIMENTO_PARCIAL",
                        "REPOSICAO_TOTAL",
                        "REPOSICAO_PARCIAL",
                        "CANCELADA",
                        "AGUARDANDO_CANCELAMENTO",
                    ],
                ),
            ),
        ),
    ]
