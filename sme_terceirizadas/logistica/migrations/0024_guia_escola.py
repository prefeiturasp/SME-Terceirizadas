# Generated by Django 2.2.13 on 2021-04-12 17:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logistica", "0023_auto_20210318_1101"),
    ]

    operations = [
        migrations.AddField(
            model_name="guia",
            name="escola",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="escola.Escola",
            ),
        ),
    ]
