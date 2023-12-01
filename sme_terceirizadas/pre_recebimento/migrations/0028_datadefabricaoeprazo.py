# Generated by Django 4.1.12 on 2023-11-08 22:51

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0027_documentoderecebimento_correcao_solicitada_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataDeFabricaoEPrazo",
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
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "data_fabricacao",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data Fabricação"
                    ),
                ),
                (
                    "data_maxima_recebimento",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data Máxima de Recebimento"
                    ),
                ),
                (
                    "prazo_maximo_recebimento",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("30", "30 dias"),
                            ("60", "60 dias"),
                            ("90", "90 dias"),
                            ("120", "120 dias"),
                            ("180", "180 dias"),
                            ("OUTRO", "Outro"),
                        ],
                        max_length=5,
                        verbose_name="Prazo Máximo para Recebimento",
                    ),
                ),
                (
                    "justificativa",
                    models.TextField(blank=True, verbose_name="Justificativa"),
                ),
                (
                    "documento_recebimento",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="datas_fabricacao_e_prazos",
                        to="pre_recebimento.documentoderecebimento",
                    ),
                ),
            ],
            options={
                "verbose_name": "Data de Fabricação e Prazo",
                "verbose_name_plural": "Datas de Fabricação e Prazos",
            },
        ),
    ]
