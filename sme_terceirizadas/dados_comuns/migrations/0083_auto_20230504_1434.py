# Generated by Django 3.2.16 on 2023-05-04 14:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pre_recebimento", "0010_auto_20230427_1014"),
        ("dados_comuns", "0082_alter_logsolicitacoesusuario_status_evento"),
    ]

    operations = [
        migrations.AddField(
            model_name="notificacao",
            name="cronograma",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notificacoes_do_cronograma",
                to="pre_recebimento.cronograma",
            ),
        ),
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
                ],
                max_length=30,
                verbose_name="Categoria",
            ),
        ),
    ]
