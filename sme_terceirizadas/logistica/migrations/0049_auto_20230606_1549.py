# Generated by Django 3.2.18 on 2023-06-06 15:49

import uuid

import django.db.models.deletion
import django_xworkflows.models
from django.db import migrations, models

import sme_terceirizadas.dados_comuns.behaviors


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0013_auto_20230112_1152"),
        ("logistica", "0048_alter_conferenciaindividualporalimento_ocorrencia"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificacaoOcorrenciasGuia",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "alterado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Alterado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "status",
                    django_xworkflows.models.StateField(
                        max_length=16,
                        workflow=django_xworkflows.models._SerializedWorkflow(
                            initial_state="RASCUNHO",
                            name="NotificacaoOcorrenciaWorkflow",
                            states=["RASCUNHO"],
                        ),
                    ),
                ),
                (
                    "numero",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        unique=True,
                        verbose_name="Número da Notificação",
                    ),
                ),
                (
                    "processo_sei",
                    models.CharField(max_length=20, verbose_name="Nº do Processo SEI"),
                ),
                (
                    "link_processo_sei",
                    models.URLField(max_length=20, verbose_name="Link do Processo SEI"),
                ),
                (
                    "distribuidor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="notificacoes",
                        to="terceirizada.terceirizada",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notificação de Guias com Ocorrencias",
                "verbose_name_plural": "Notificações de Guias com Ocorrencias",
            },
            bases=(
                sme_terceirizadas.dados_comuns.behaviors.TemIdentificadorExternoAmigavel,
                sme_terceirizadas.dados_comuns.behaviors.Logs,
                django_xworkflows.models.BaseWorkflowEnabled,
                models.Model,
            ),
        ),
        migrations.AddField(
            model_name="guia",
            name="notificacao",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="guias_notificadas",
                to="logistica.notificacaoocorrenciasguia",
            ),
        ),
    ]
