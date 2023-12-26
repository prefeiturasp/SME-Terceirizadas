# Generated by Django 4.2.7 on 2023-12-22 11:39

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0066_codae_acesso_modulo_medicao_inicial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GrupoUnidadeEscolar",
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
                    "nome",
                    models.CharField(blank=True, max_length=100, verbose_name="Nome"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "tipos_unidades",
                    models.ManyToManyField(blank=True, to="escola.tipounidadeescolar"),
                ),
            ],
            options={
                "verbose_name": "Grupo de unidade escolar",
                "verbose_name_plural": "Grupos de unidade escolar",
                "ordering": ("nome",),
            },
        ),
    ]
