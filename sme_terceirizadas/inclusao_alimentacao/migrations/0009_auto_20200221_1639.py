# Generated by Django 2.2.8 on 2020-02-21 19:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inclusao_alimentacao', '0008_auto_20200219_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quantidadedealunosporfaixaetariadainclusaodealimentacaodacei',
            name='inclusao_alimentacao_da_cei',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quantidade_alunos_da_inclusao', to='inclusao_alimentacao.InclusaoAlimentacaoDaCEI'),
        ),
    ]
