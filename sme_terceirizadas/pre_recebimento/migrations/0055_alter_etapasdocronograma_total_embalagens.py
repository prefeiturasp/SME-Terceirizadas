# Generated by Django 4.2.7 on 2024-04-01 17:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0054_alter_layoutdeembalagem_ficha_tecnica"),
    ]

    operations = [
        migrations.AlterField(
            model_name="etapasdocronograma",
            name="total_embalagens",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Total de Embalagens"
            ),
        ),
    ]
