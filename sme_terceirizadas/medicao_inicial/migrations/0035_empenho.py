# Generated by Django 4.2.7 on 2024-02-06 10:33

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0019_alter_contrato_ata"),
        (
            "medicao_inicial",
            "0034_solicitacaomedicaoinicial_dre_ciencia_correcao_data_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Empenho",
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
                    "numero",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Número do empenho"
                    ),
                ),
                (
                    "tipo_empenho",
                    models.CharField(
                        choices=[("PRINCIPAL", "Principal"), ("REAJUSTE", "Reajuste")],
                        default="PRINCIPAL",
                        max_length=20,
                    ),
                ),
                (
                    "tipo_reajuste",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("ALIMENTACOES", "Alimentações"),
                            ("DIETAS", "Dietas"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("ATIVO", "Ativo"), ("INATIVO", "Inativo")],
                        default="ATIVO",
                        max_length=10,
                    ),
                ),
                ("valor_total", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "contrato",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="empenhos",
                        to="terceirizada.contrato",
                    ),
                ),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="empenhos",
                        to="terceirizada.edital",
                    ),
                ),
            ],
            options={
                "verbose_name": "Empenho",
                "verbose_name_plural": "Empenhos",
                "ordering": ["-alterado_em"],
            },
        ),
    ]
