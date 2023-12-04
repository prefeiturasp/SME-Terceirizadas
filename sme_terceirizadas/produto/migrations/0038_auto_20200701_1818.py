# Generated by Django 2.2.10 on 2020-07-01 21:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("produto", "0037_merge_20200624_1241"),
    ]

    operations = [
        migrations.AlterField(
            model_name="respostaanalisesensorial",
            name="homologacao_de_produto",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="respostas_analise",
                to="produto.HomologacaoDoProduto",
            ),
        ),
    ]
