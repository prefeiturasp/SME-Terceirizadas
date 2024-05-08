# Generated by Django 4.2.7 on 2024-05-07 16:16

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0020_edital_eh_imr"),
        ("imr", "0015_tipoocorrencia_aceita_multiplas_respostas"),
    ]

    operations = [
        migrations.CreateModel(
            name="UtensilioCozinha",
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
                "verbose_name": "Utensílio de Cozinha",
                "verbose_name_plural": "Utensílios de Cozinha",
                "ordering": ("nome",),
            },
        ),
        migrations.CreateModel(
            name="EditalUtensilioCozinha",
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
                    "utensilios_cozinha",
                    models.ManyToManyField(
                        blank=True,
                        to="imr.utensiliocozinha",
                        verbose_name="Utensílios de Cozinha",
                    ),
                ),
            ],
            options={
                "verbose_name": "Utensílio de Cozinha Por Edital",
                "verbose_name_plural": "Utensílios de Cozinha Por Edital",
            },
        ),
    ]
