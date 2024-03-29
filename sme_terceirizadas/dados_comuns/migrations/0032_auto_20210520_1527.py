# Generated by Django 2.2.13 on 2021-05-20 15:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0031_auto_20210520_1450"),
    ]

    operations = [
        migrations.AlterField(
            model_name="templatemensagem",
            name="tipo",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Alteração do tipo de Alimentação"),
                    (1, "Inclusão de alimentação"),
                    (2, "Inclusão de alimentação contínua"),
                    (3, "Suspensão de alimentação"),
                    (4, "Solicitação de kit lanche avulsa"),
                    (5, "Solicitação de kit lanche unificada"),
                    (6, "Inversão de cardápio"),
                    (7, "Dieta Especial"),
                    (8, "Homologação de Produto"),
                ],
                unique=True,
            ),
        ),
    ]
