# Generated by Django 2.2.13 on 2022-10-20 14:53

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("terceirizada", "0007_auto_20211008_1027"),
    ]

    operations = [
        migrations.CreateModel(
            name="Modulo",
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
                ("nome", models.CharField(max_length=100, verbose_name="Nome")),
            ],
            options={
                "verbose_name": "Módulo",
                "verbose_name_plural": "Módulos",
            },
        ),
        migrations.CreateModel(
            name="EmailTerceirizadaPorModulo",
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
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="E-mail"
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "criado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="emails_terceirizadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modulo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emails_terceirizadas",
                        to="terceirizada.Modulo",
                    ),
                ),
                (
                    "terceirizada",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emails_terceirizadas",
                        to="terceirizada.Terceirizada",
                    ),
                ),
            ],
            options={
                "verbose_name": "E-mail de Terceirizada por Módulos",
                "verbose_name_plural": "E-mails de Terceirizadas por Módulos",
            },
        ),
    ]
