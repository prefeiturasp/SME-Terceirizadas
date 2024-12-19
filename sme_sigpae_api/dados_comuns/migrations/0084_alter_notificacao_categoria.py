# Generated by Django 3.2.16 on 2023-05-11 09:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0083_auto_20230504_1434"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificacao",
            name="categoria",
            field=models.CharField(
                choices=[
                    ("REQUISICAO_DE_ENTREGA", "Requisição de entrega"),
                    (
                        "ALTERACAO_REQUISICAO_ENTREGA",
                        "Alteração de requisição de entrega",
                    ),
                    ("GUIA_DE_REMESSA", "Guia de Remessa"),
                    ("CRONOGRAMA", "Assinatura do Cronograma"),
                    ("ALTERACAO_CRONOGRAMA", "Solicitação de Alteração do Cronograma"),
                ],
                max_length=30,
                verbose_name="Categoria",
            ),
        ),
    ]