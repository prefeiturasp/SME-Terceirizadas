# Generated by Django 2.2.13 on 2022-04-14 09:40

import uuid

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logistica", "0043_auto_20211020_1414"),
    ]

    operations = [
        migrations.CreateModel(
            name="LogSolicitacaoDeCancelamentoPeloPapa",
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
                    "guias",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=100), size=None
                    ),
                ),
                (
                    "sequencia_envio",
                    models.IntegerField(
                        verbose_name="Sequência de envio atribuída pelo papa"
                    ),
                ),
                ("foi_confirmada", models.BooleanField(default=False)),
                (
                    "requisicao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitacoes_de_cancelamento",
                        to="logistica.SolicitacaoRemessa",
                    ),
                ),
            ],
            options={
                "verbose_name": "Log de Solicitação de Cancelamento do PAPA",
                "verbose_name_plural": "Logs de Solicitações de Cancelamento do PAPA",
            },
        ),
    ]
