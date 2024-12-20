# Generated by Django 4.2.7 on 2024-06-11 14:57

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("imr", "0028_anexosformulariobase_nome_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formulariosupervisao",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=27,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="EM_PREENCHIMENTO",
                    name="FormularioSupervisaoWorkflow",
                    states=["EM_PREENCHIMENTO", "NUTRIMANIFESTACAO_A_VALIDAR"],
                ),
            ),
        ),
    ]
