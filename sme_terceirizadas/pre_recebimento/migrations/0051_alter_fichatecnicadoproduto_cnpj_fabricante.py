# Generated by Django 4.2.7 on 2024-02-09 12:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0050_analisefichatecnica"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fichatecnicadoproduto",
            name="cnpj_fabricante",
            field=models.CharField(
                blank=True,
                max_length=14,
                validators=[django.core.validators.MinLengthValidator(14)],
                verbose_name="CNPJ",
            ),
        ),
    ]
