# Generated by Django 2.2.13 on 2021-10-25 22:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0040_auto_20211025_1957"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contato",
            name="telefone",
            field=models.CharField(
                blank=True,
                max_length=10,
                validators=[django.core.validators.MinLengthValidator(8)],
            ),
        ),
    ]
