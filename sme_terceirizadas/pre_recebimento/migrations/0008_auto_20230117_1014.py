# Generated by Django 2.2.13 on 2023-01-17 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0074_auto_20221207_0844'),
        ('terceirizada', '0013_auto_20230112_1152'),
        ('pre_recebimento', '0007_embalagemqld'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cronograma',
            name='contrato',
        ),
        migrations.RemoveField(
            model_name='cronograma',
            name='contrato_uuid',
        ),
        migrations.RemoveField(
            model_name='cronograma',
            name='empresa_uuid',
        ),
        migrations.RemoveField(
            model_name='cronograma',
            name='nome_empresa',
        ),
        migrations.RemoveField(
            model_name='cronograma',
            name='nome_produto',
        ),
        migrations.RemoveField(
            model_name='cronograma',
            name='processo_sei',
        ),
        migrations.RemoveField(
            model_name='cronograma',
            name='produto_uuid',
        ),
        migrations.RemoveField(
            model_name='cronograma',
            name='unidade_medida',
        ),
        migrations.RemoveField(
            model_name='etapasdocronograma',
            name='empenho_uuid',
        ),
        migrations.AddField(
            model_name='cronograma',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='terceirizada.Terceirizada'),
        ),
        migrations.AddField(
            model_name='cronograma',
            name='produto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='produto.ProdutoEdital'),
        ),
    ]
