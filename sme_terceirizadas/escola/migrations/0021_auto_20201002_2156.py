# Generated by Django 2.2.13 on 2020-10-02 21:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0020_auto_20201002_2051"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aluno",
            name="codigo_eol",
            field=models.CharField(
                blank=True,
                max_length=7,
                null=True,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(7)],
                verbose_name="Código EOL",
            ),
        ),
    ]
