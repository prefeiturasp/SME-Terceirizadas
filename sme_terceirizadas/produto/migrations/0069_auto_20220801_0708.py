# Generated by Django 2.2.13 on 2022-08-01 07:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0068_auto_20220729_0455"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produtoedital",
            name="edital",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="vinculos",
                to="terceirizada.Edital",
            ),
        ),
        migrations.AlterField(
            model_name="produtoedital",
            name="produto",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="vinculos",
                to="produto.Produto",
            ),
        ),
    ]
