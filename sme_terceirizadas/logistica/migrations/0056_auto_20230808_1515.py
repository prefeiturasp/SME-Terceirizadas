# Generated by Django 3.2.18 on 2023-08-08 15:15

import django_xworkflows.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logistica", "0055_alter_notificacaoocorrenciasguia_processo_sei"),
    ]

    operations = [
        migrations.AddField(
            model_name="previsaocontratualnotificacao",
            name="aprovado",
            field=models.BooleanField(default=False, verbose_name="Aprovado"),
        ),
        migrations.AddField(
            model_name="previsaocontratualnotificacao",
            name="justificativa_alteracao",
            field=models.TextField(
                blank=True, max_length=500, verbose_name="Justificativa da Alteração"
            ),
        ),
        migrations.AlterField(
            model_name="notificacaoocorrenciasguia",
            name="status",
            field=django_xworkflows.models.StateField(
                max_length=32,
                workflow=django_xworkflows.models._SerializedWorkflow(
                    initial_state="RASCUNHO",
                    name="NotificacaoOcorrenciaWorkflow",
                    states=[
                        "RASCUNHO",
                        "NOTIFICACAO_CRIADA",
                        "NOTIFICACAO_ENVIADA_FISCAL",
                        "NOTIFICACAO_SOLICITADA_ALTERACAO",
                        "NOTIFICACAO_ASSINADA_FISCAL",
                    ],
                ),
            ),
        ),
    ]
