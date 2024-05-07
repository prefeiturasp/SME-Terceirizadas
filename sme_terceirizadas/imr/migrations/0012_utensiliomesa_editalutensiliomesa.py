# Generated by Django 4.2.7 on 2024-05-06 10:50

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0020_edital_eh_imr"),
        ("imr", "0011_respostanaoseaplica"),
    ]

    operations = [
        migrations.CreateModel(
            name="UtensilioMesa",
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
                "verbose_name": "Utensílio de Mesa",
                "verbose_name_plural": "Utensílios de Mesa",
                "ordering": ("nome",),
            },
        ),
        migrations.CreateModel(
            name="EditalUtensilioMesa",
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
                    "utensilios_mesa",
                    models.ManyToManyField(
                        blank=True,
                        to="imr.utensiliomesa",
                        verbose_name="Utensílios de Mesa",
                    ),
                ),
            ],
            options={
                "verbose_name": "Utensílio de Mesa Por Edital",
                "verbose_name_plural": "Utensílios de Mesa Por Edital",
            },
        ),
    ]