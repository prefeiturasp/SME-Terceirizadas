# Generated by Django 4.2.7 on 2024-03-13 13:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0053_remove_layoutdeembalagem_cronograma_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="layoutdeembalagem",
            name="ficha_tecnica",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="layout_embalagem",
                to="pre_recebimento.fichatecnicadoproduto",
            ),
        ),
    ]