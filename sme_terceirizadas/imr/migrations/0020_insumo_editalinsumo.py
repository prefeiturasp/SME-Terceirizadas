# Generated by Django 4.2.7 on 2024-05-09 16:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0020_edital_eh_imr"),
        ("imr", "0019_reparoeadaptacao_editalreparoeadaptacao"),
    ]

    operations = [
        migrations.CreateModel(
            name="Insumo",
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
                    models.CharField(blank=True, max_length=250, verbose_name="Nome"),
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
            ],
            options={
                "verbose_name": "Insumo",
                "verbose_name_plural": "Insumos",
                "ordering": ("nome",),
            },
        ),
        migrations.CreateModel(
            name="EditalInsumo",
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
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="terceirizada.edital",
                    ),
                ),
                (
                    "insumos",
                    models.ManyToManyField(
                        blank=True, to="imr.insumo", verbose_name="Insumos"
                    ),
                ),
            ],
            options={
                "verbose_name": "Insumo Por Edital",
                "verbose_name_plural": "Insumos Por Edital",
            },
        ),
    ]
