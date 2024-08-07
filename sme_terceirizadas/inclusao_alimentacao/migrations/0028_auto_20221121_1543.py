# Generated by Django 2.2.13 on 2022-11-21 15:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inclusao_alimentacao", "0027_auto_20221104_2024"),
    ]

    operations = [
        migrations.AddField(
            model_name="quantidadedealunosporfaixaetariadainclusaodealimentacaodacei",
            name="matriculados_quando_criado",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
        migrations.AlterField(
            model_name="quantidadedealunosemeiinclusaodealimentacaocemei",
            name="matriculados_quando_criado",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
        migrations.AlterField(
            model_name="quantidadedealunosporfaixaetariadainclusaodealimentacaocemei",
            name="matriculados_quando_criado",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
    ]
