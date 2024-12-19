# Generated by Django 4.2.7 on 2024-03-28 15:49

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "pre_recebimento",
            "0055_remove_documentoderecebimento_data_fabricacao_lote_and_more",
        ),
        ("recebimento", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuestoesPorProduto",
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
                    "ficha_tecnica",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questoes_conferencia",
                        to="pre_recebimento.fichatecnicadoproduto",
                    ),
                ),
                (
                    "questoes_primarias",
                    models.ManyToManyField(
                        related_name="questoes_primarias",
                        to="recebimento.questaoconferencia",
                        verbose_name="Questões referentes à Embalagem Primária",
                    ),
                ),
                (
                    "questoes_secundarias",
                    models.ManyToManyField(
                        related_name="questoes_secundarias",
                        to="recebimento.questaoconferencia",
                        verbose_name="Questões referentes à Embalagem Secundária",
                    ),
                ),
            ],
            options={
                "verbose_name": "Questões por Produto",
                "verbose_name_plural": "Questões por Produtos",
            },
        ),
    ]