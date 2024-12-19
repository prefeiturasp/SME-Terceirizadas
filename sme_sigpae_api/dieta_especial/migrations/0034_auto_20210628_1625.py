# Generated by Django 2.2.13 on 2021-06-28 16:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dieta_especial", "0033_protocolopadraodietaespecial_orientacoes_gerais"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitacaodietaespecial",
            name="orientacoes_gerais",
            field=models.TextField(blank=True, verbose_name="Orientações Gerais"),
        ),
        migrations.AddField(
            model_name="solicitacaodietaespecial",
            name="protocolo_padrao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="solicitacoes_dietas_especiais",
                to="dieta_especial.ProtocoloPadraoDietaEspecial",
            ),
        ),
    ]