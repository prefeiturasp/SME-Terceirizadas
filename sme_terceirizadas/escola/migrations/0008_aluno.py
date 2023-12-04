# Generated by Django 2.2.8 on 2020-01-20 14:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0007_auto_20200110_1052"),
    ]

    operations = [
        migrations.CreateModel(
            name="Aluno",
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
                    models.CharField(
                        max_length=100, verbose_name="Nome Completo do Aluno"
                    ),
                ),
                (
                    "codigo_eol",
                    models.CharField(
                        max_length=6, unique=True, verbose_name="Código EOL"
                    ),
                ),
                ("data_nascimento", models.DateField()),
                (
                    "escola",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="escola.Escola",
                    ),
                ),
            ],
            options={
                "verbose_name": "Aluno",
                "verbose_name_plural": "Alunos",
            },
        ),
    ]
