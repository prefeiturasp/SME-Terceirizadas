# Generated by Django 4.2.7 on 2023-12-19 11:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0017_alter_contrato_numero"),
        ("produto", "0081_alter_homologacaoproduto_rastro_terceirizada"),
        ("pre_recebimento", "0033_alter_fichatecnicadoproduto_agroecologico_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="fichatecnicadoproduto",
            name="porcao",
            field=models.CharField(blank=True, max_length=50, verbose_name="Porção"),
        ),
        migrations.AddField(
            model_name="fichatecnicadoproduto",
            name="unidade_medida",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fichas_tecnicas",
                to="pre_recebimento.unidademedida",
            ),
        ),
        migrations.AddField(
            model_name="fichatecnicadoproduto",
            name="unidade_medida_caseira",
            field=models.CharField(
                blank=True, max_length=100, verbose_name="Unidade de Medida Caseira"
            ),
        ),
        migrations.AddField(
            model_name="fichatecnicadoproduto",
            name="valor_unidade_caseira",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="Unidade Caseira"
            ),
        ),
        migrations.AlterField(
            model_name="fichatecnicadoproduto",
            name="empresa",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="fichas_tecnicas",
                to="terceirizada.terceirizada",
            ),
        ),
        migrations.AlterField(
            model_name="fichatecnicadoproduto",
            name="fabricante",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fichas_tecnicas",
                to="produto.fabricante",
            ),
        ),
        migrations.AlterField(
            model_name="fichatecnicadoproduto",
            name="produto",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fichas_tecnicas",
                to="produto.nomedeprodutoedital",
            ),
        ),
    ]
