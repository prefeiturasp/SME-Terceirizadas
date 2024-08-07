# Generated by Django 4.2.7 on 2024-06-25 23:23

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("imr", "0031_alter_tipoocorrencia_options"),
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
                    states=[
                        "EM_PREENCHIMENTO",
                        "NUTRIMANIFESTACAO_A_VALIDAR",
                        "COM_COMENTARIOS_DE_CODAE",
                        "VALIDADO_POR_CODAE",
                        "APROVADO",
                    ],
                ),
            ),
        ),
    ]
