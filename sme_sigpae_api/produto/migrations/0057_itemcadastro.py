# Generated by Django 2.2.13 on 2021-08-26 19:52

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("produto", "0056_auto_20210821_0144"),
    ]

    operations = [
        migrations.CreateModel(
            name="ItemCadastro",
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
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("MARCA", "Marca"),
                            ("FABRICANTE", "Fabricante"),
                            ("UNIDADE_MEDIDA", "Unidade de Medida"),
                            ("EMBALAGEM", "Embalagem"),
                        ],
                        max_length=30,
                        verbose_name="Tipo",
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]