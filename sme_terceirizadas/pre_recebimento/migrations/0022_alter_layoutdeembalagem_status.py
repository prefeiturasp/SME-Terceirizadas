# Generated by Django 3.2.20 on 2023-10-02 15:31

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "pre_recebimento",
            "0021_imagemdotipodeembalagem_layoutdeembalagem_tipodeembalagemdelayout",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="layoutdeembalagem",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=20,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="LAYOUT_CRIADO",
                    name="LayoutDeEmbalagemWorkflow",
                    states=[
                        "LAYOUT_CRIADO",
                        "ENVIADO_PARA_ANALISE",
                        "APROVADO",
                        "SOLICITADO_CORRECAO",
                    ],
                ),
            ),
        ),
    ]
