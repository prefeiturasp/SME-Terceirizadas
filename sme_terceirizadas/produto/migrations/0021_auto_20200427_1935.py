# Generated by Django 2.2.10 on 2020-04-27 22:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0020_auto_20200427_1920"),
    ]

    operations = [
        migrations.AlterField(
            model_name="informacoesnutricionaisdoproduto",
            name="valor_diario",
            field=models.IntegerField(),
        ),
    ]
