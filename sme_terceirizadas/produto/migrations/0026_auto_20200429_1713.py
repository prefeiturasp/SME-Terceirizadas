# Generated by Django 2.2.10 on 2020-04-29 20:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0025_auto_20200427_2111"),
    ]

    operations = [
        migrations.AlterField(
            model_name="informacoesnutricionaisdoproduto",
            name="valor_diario",
            field=models.CharField(max_length=10),
        ),
    ]
