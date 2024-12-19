# Generated by Django 2.2.13 on 2022-07-18 18:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0051_auto_20220718_0545"),
    ]

    operations = [
        migrations.AlterField(
            model_name="periodoescolar",
            name="posicao",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
    ]