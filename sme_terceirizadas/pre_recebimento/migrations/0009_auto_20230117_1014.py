# Generated by Django 2.2.13 on 2023-01-17 10:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terceirizada', '0013_auto_20230112_1152'),
        ('produto', '0074_auto_20221207_0844'),
        ('pre_recebimento', '0008_auto_20230117_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='cronograma',
            name='contrato',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='terceirizada.Contrato'),
        ),
        migrations.AddField(
            model_name='cronograma',
            name='unidade_medida',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='produto.UnidadeMedida'),
        ),
    ]
