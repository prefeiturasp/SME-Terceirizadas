# Generated by Django 4.2.7 on 2024-01-08 14:27

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0038_fichatecnicadoproduto_produto_eh_liquido_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fichatecnicadoproduto",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=20,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="FichaTecnicaDoProdutoWorkflow",
                    states=["RASCUNHO", "ENVIADA_PARA_ANALISE"],
                ),
            ),
        ),
    ]
