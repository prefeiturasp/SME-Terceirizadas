# Generated by Django 2.2.6 on 2019-12-06 14:13

import django_xworkflows.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kit_lanche", "0002_auto_20191205_1815"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacaokitlancheavulsa",
            name="foi_solicitado_fora_do_prazo",
            field=models.BooleanField(
                default=False,
                verbose_name="Solicitação foi criada em cima da hora (5 dias úteis ou menos)?",
            ),
        ),
        migrations.AlterField(
            model_name="solicitacaokitlancheavulsa",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=37,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="PedidoAPartirDaEscolaWorkflow",
                    states=[
                        "RASCUNHO",
                        "DRE_A_VALIDAR",
                        "DRE_VALIDADO",
                        "DRE_PEDIU_ESCOLA_REVISAR",
                        "DRE_NAO_VALIDOU_PEDIDO_ESCOLA",
                        "CODAE_AUTORIZADO",
                        "CODAE_QUESTIONADO",
                        "CODAE_NEGOU_PEDIDO",
                        "TERCEIRIZADA_RESPONDEU_QUESTIONAMENTO",
                        "TERCEIRIZADA_TOMOU_CIENCIA",
                        "ESCOLA_CANCELOU",
                        "CANCELADO_AUTOMATICAMENTE",
                    ],
                ),
            ),
        ),
    ]
