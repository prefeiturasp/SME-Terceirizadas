# Generated by Django 2.2.13 on 2021-04-15 17:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logistica", "0024_guia_escola"),
    ]

    operations = [
        migrations.AlterField(
            model_name="guia",
            name="escola",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="escola.Escola",
            ),
        ),
    ]
