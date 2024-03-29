# Generated by Django 3.2.20 on 2023-09-19 11:28

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("escola", "0061_alter_logalunosmatriculadosperiodoescola_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiaSuspensaoAtividades",
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
                ("data", models.DateField(verbose_name="Data")),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
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
                    "tipo_unidade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="escola.tipounidadeescolar",
                    ),
                ),
            ],
            options={
                "verbose_name": "Dia de suspensão de atividades",
                "verbose_name_plural": "Dias de suspensão de atividades",
                "ordering": ("data",),
                "unique_together": {("tipo_unidade", "data")},
            },
        ),
    ]
