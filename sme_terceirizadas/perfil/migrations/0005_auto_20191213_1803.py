# Generated by Django 2.2.6 on 2019-12-13 21:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("perfil", "0004_auto_20191213_1800"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usuario",
            name="registro_funcional",
            field=models.CharField(
                max_length=7,
                null=True,
                unique=True,
                validators=[django.core.validators.MinLengthValidator(7)],
                verbose_name="RF",
            ),
        ),
    ]
