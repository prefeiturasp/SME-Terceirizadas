# Generated by Django 2.2.10 on 2020-04-22 21:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0010_auto_20200420_1754"),
    ]

    operations = [
        migrations.AlterField(
            model_name="imagemdoproduto",
            name="produto",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="produto.Produto"
            ),
        ),
    ]
