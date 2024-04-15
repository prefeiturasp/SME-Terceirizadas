# Generated by Django 4.2.7 on 2024-04-09 19:50

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("terceirizada", "0019_alter_contrato_ata"),
    ]

    operations = [
        migrations.CreateModel(
            name="TipoGravidade",
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
                ("tipo", models.CharField(verbose_name="Tipo de Gravidade")),
            ],
            options={
                "verbose_name": "Tipo de Gravidade",
                "verbose_name_plural": "Tipos de Gravidades",
            },
        ),
        migrations.CreateModel(
            name="TipoPenalidade",
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
                    "numero_clausula",
                    models.CharField(
                        max_length=300, verbose_name="Número da Cláusula/Item"
                    ),
                ),
                (
                    "descricao",
                    models.TextField(verbose_name="Descrição da Cláusula/Item"),
                ),
                (
                    "status",
                    models.BooleanField(
                        choices=[(True, "Ativo"), (False, "Inativo")],
                        default=True,
                        verbose_name="Status",
                    ),
                ),
                (
                    "criado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tipos_penalidades",
                        to="terceirizada.edital",
                    ),
                ),
                (
                    "gravidade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tipos_penalidades",
                        to="imr.tipogravidade",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tipo de Penalidade",
                "verbose_name_plural": "Tipos de Penalidades",
            },
        ),
        migrations.CreateModel(
            name="ObrigacaoPenalidade",
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
                    "descricao",
                    models.CharField(max_length=300, verbose_name="Descrição"),
                ),
                (
                    "tipo_penalidade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="obrigacoes",
                        to="imr.tipopenalidade",
                    ),
                ),
            ],
            options={
                "verbose_name": "Obrigação da Penalidade",
                "verbose_name_plural": "Obrigações das Penalidades",
            },
        ),
    ]
