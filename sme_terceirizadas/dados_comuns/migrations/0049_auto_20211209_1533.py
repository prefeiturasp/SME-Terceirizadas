# Generated by Django 2.2.13 on 2021-12-09 15:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logistica", "0043_auto_20211020_1414"),
        ("dados_comuns", "0048_notificacao_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificacao",
            name="guia",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notificacoes_da_guia",
                to="logistica.Guia",
            ),
        ),
        migrations.AlterField(
            model_name="notificacao",
            name="descricao",
            field=models.TextField(
                blank=True, default="", max_length=5000, verbose_name="Descrição"
            ),
        ),
    ]
