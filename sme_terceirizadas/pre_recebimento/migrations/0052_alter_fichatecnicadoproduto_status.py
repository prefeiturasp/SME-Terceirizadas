# Generated by Django 4.2.7 on 2024-02-09 13:19

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0051_alter_fichatecnicadoproduto_cnpj_fabricante"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fichatecnicadoproduto",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=21,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="FichaTecnicaDoProdutoWorkflow",
                    states=[
                        "RASCUNHO",
                        "ENVIADA_PARA_ANALISE",
                        "APROVADA",
                        "ENVIADA_PARA_CORRECAO",
                    ],
                ),
            ),
        ),
    ]
