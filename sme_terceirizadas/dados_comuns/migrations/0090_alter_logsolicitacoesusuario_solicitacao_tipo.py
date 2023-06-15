# Generated by Django 3.2.18 on 2023-06-05 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dados_comuns', '0089_alter_logsolicitacoesusuario_status_evento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logsolicitacoesusuario',
            name='solicitacao_tipo',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Solicitação de kit lanche avulsa'), (1, 'Alteração do tipo de alimentação'), (2, 'Suspensão de cardápio'), (3, 'Inversão de cardápio'), (4, 'Inclusão de alimentação normal'), (5, 'Inclusão de alimentação da CEI'), (6, 'Suspensão de alimentação da CEI'), (7, 'Inclusão de alimentação contínua'), (8, 'Dieta Especial'), (9, 'Solicitação de kit lanche unificada'), (10, 'Homologação de Produto'), (11, 'Reclamação de Produto'), (34, 'Responde Análise Sensorial'), (12, 'Solicitação de remessa'), (13, 'Solicitação de Ateração de requisição'), (14, 'Abastecimento de guia de remessa'), (15, 'Solicitação de medição inicial'), (16, 'Inclusão de Alimentação CEMEI'), (17, 'Solicitação de kit lanche CEMEI'), (18, 'Cronograma'), (19, 'Solicitação de alteração do cronograma'), (20, 'Notificação de guia com ocorrência')]),
        ),
    ]