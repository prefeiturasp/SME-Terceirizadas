# Generated by Django 2.2.8 on 2020-04-20 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0007_auto_20200420_1309"),
    ]

    operations = [
        migrations.AlterField(
            model_name="informacoesnutricionaisdoproduto",
            name="produto",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="informacoes_nutricionais",
                to="produto.Produto",
            ),
        ),
    ]
