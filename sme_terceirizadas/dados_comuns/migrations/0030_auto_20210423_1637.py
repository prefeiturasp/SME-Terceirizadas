# Generated by Django 2.2.13 on 2021-04-23 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dados_comuns', '0029_auto_20210305_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logsolicitacoesusuario',
            name='solicitacao_tipo',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Solicitação de kit lanche avulsa'), (1, 'Alteração de cardápio'), (2, 'Suspensão de cardápio'), (3, 'Inversão de cardápio'), (4, 'Inclusão de alimentação normal'), (5, 'Inclusão de alimentação da CEI'), (6, 'Suspensão de alimentação da CEI'), (7, 'Inclusão de alimentação contínua'), (8, 'Dieta Especial'), (9, 'Solicitação de kit lanche unificada'), (10, 'Homologação de Produto'), (11, 'Reclamação de Produto'), (31, 'Responde Análise Sensorial'), (12, 'Solicitação de remessa'), (13, 'Solicitação de Ateração de requisição'), (14, 'Abastecimento de guia de remessa')]),
        ),
    ]
