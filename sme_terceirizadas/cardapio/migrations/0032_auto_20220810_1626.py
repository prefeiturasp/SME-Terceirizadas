# Generated by Django 2.2.13 on 2022-08-10 16:26

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0031_suspensaoalimentacaodacei_terceirizada_conferiu_gestao"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gruposuspensaoalimentacao",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=26,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="InformativoPartindoDaEscolaWorkflow",
                    states=[
                        "RASCUNHO",
                        "INFORMADO",
                        "TERCEIRIZADA_TOMOU_CIENCIA",
                        "ESCOLA_CANCELOU",
                    ],
                ),
            ),
        ),
        migrations.AlterField(
            model_name="suspensaoalimentacaodacei",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=26,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="InformativoPartindoDaEscolaWorkflow",
                    states=[
                        "RASCUNHO",
                        "INFORMADO",
                        "TERCEIRIZADA_TOMOU_CIENCIA",
                        "ESCOLA_CANCELOU",
                    ],
                ),
            ),
        ),
    ]
