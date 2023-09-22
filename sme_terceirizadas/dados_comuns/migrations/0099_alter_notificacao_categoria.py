# Generated by Django 3.2.18 on 2023-09-18 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dados_comuns', '0098_altualizar_notificacoes_antigas_alteracao_cronograma'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificacao',
            name='categoria',
            field=models.CharField(choices=[('REQUISICAO_DE_ENTREGA', 'Requisição de entrega'), ('ALTERACAO_REQUISICAO_ENTREGA', 'Alteração de requisição de entrega'), ('GUIA_DE_REMESSA', 'Guia de Remessa'), ('CRONOGRAMA', 'Assinatura do Cronograma'), ('SOLICITACAO_ALTERACAO_CRONOGRAMA', 'Solicitação de Alteração do Cronograma'), ('ALTERACAO_CRONOGRAMA', 'Alteração do Cronograma')], max_length=50, verbose_name='Categoria'),
        ),
    ]
