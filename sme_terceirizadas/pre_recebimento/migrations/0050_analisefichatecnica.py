# Generated by Django 4.2.7 on 2024-02-05 08:38

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pre_recebimento", "0049_remove_cronograma_produto"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnaliseFichaTecnica",
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
                ("detalhes_produto_conferido", models.BooleanField(null=True)),
                ("detalhes_produto_correcoes", models.TextField(blank=True)),
                ("informacoes_nutricionais_conferido", models.BooleanField(null=True)),
                ("informacoes_nutricionais_correcoes", models.TextField(blank=True)),
                ("conservacao_conferido", models.BooleanField(null=True)),
                ("conservacao_correcoes", models.TextField(blank=True)),
                ("temperatura_e_transporte_conferido", models.BooleanField(null=True)),
                ("temperatura_e_transporte_correcoes", models.TextField(blank=True)),
                ("armazenamento_conferido", models.BooleanField(null=True)),
                ("armazenamento_correcoes", models.TextField(blank=True)),
                ("embalagem_e_rotulagem_conferido", models.BooleanField(null=True)),
                ("embalagem_e_rotulagem_correcoes", models.TextField(blank=True)),
                ("responsavel_tecnico_conferido", models.BooleanField(null=True)),
                ("modo_preparo_conferido", models.BooleanField(null=True)),
                ("outras_informacoes_conferido", models.BooleanField(null=True)),
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
                    "ficha_tecnica",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analises",
                        to="pre_recebimento.fichatecnicadoproduto",
                    ),
                ),
            ],
            options={
                "verbose_name": "Análise da Ficha Técnica",
                "verbose_name_plural": "Análises das Fichas Técnicas",
            },
        ),
    ]
