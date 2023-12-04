# Generated by Django 2.2.13 on 2020-09-23 10:16

import django.core.validators
import django_prometheus.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0021_auto_20200827_1449"),
    ]

    operations = [
        migrations.CreateModel(
            name="Endereco",
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
                    "logradouro",
                    models.CharField(
                        max_length=255,
                        validators=[django.core.validators.MinLengthValidator(5)],
                    ),
                ),
                ("numero", models.IntegerField(null=True)),
                ("complemento", models.CharField(blank=True, max_length=50)),
                ("bairro", models.CharField(max_length=50)),
                ("cep", models.IntegerField()),
            ],
            bases=(
                django_prometheus.models.ExportModelOperationsMixin("endereco"),
                models.Model,
            ),
        ),
    ]
