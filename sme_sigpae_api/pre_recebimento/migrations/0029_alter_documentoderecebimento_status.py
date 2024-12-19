# Generated by Django 4.1.12 on 2023-11-10 10:21

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0028_datadefabricaoeprazo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentoderecebimento",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=21,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="DOCUMENTO_CRIADO",
                    name="DocumentoDeRecebimentoWorkflow",
                    states=[
                        "DOCUMENTO_CRIADO",
                        "ENVIADO_PARA_ANALISE",
                        "ENVIADO_PARA_CORRECAO",
                        "APROVADO",
                    ],
                ),
            ),
        ),
    ]