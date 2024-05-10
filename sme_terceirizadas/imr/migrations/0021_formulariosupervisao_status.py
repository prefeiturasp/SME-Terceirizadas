# Generated by Django 4.2.7 on 2024-05-10 16:34

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("imr", "0020_alter_formulariosupervisao_nome_nutricionista_empresa_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="formulariosupervisao",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=16,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="EM_PREENCHIMENTO",
                    name="FormularioSupervisaoWorkflow",
                    states=["EM_PREENCHIMENTO"],
                ),
            ),
        ),
    ]