# Generated by Django 2.2.13 on 2022-06-19 18:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("escola", "0046_subprefeitura_agrupamento"),
    ]

    operations = [
        migrations.AddField(
            model_name="escola",
            name="subprefeitura",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="escolas",
                to="escola.Subprefeitura",
            ),
        ),
    ]
