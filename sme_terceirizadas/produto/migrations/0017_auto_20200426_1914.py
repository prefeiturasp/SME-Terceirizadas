# Generated by Django 2.2.8 on 2020-04-26 22:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0016_auto_20200426_1702"),
    ]

    operations = [
        migrations.AlterField(
            model_name="informacoesnutricionaisdoproduto",
            name="quantidade_porcao",
            field=models.CharField(
                blank=True, max_length=15, verbose_name="Quantidade por Porção"
            ),
        ),
        migrations.AlterField(
            model_name="informacoesnutricionaisdoproduto",
            name="valor_diario",
            field=models.CharField(blank=True, max_length=15, verbose_name="%VD(*)"),
        ),
    ]
