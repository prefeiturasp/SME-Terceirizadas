# Generated by Django 2.2.13 on 2021-08-02 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dados_comuns', '0033_auto_20210603_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logsolicitacoesusuario',
            name='status_evento',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Solicitação Realizada'), (1, 'CODAE autorizou'), (2, 'Terceirizada tomou ciência'), (3, 'Terceirizada recusou'), (4, 'CODAE negou'), (5, 'CODAE pediu revisão'), (6, 'DRE revisou'), (7, 'DRE validou'), (8, 'DRE pediu revisão'), (9, 'DRE não validou'), (10, 'Escola revisou'), (13, 'Escola cancelou'), (14, 'DRE cancelou'), (11, 'Questionamento pela CODAE'), (12, 'Terceirizada respondeu questionamento'), (15, 'Escola solicitou inativação'), (16, 'CODAE autorizou inativação'), (17, 'CODAE negou inativação'), (18, 'Terceirizada tomou ciência da inativação'), (19, 'Cancelada por atingir data de término'), (20, 'Pendente homologação da CODAE'), (21, 'CODAE homologou'), (22, 'CODAE não homologou'), (23, 'CODAE pediu análise sensorial'), (24, 'Terceirizada cancelou homologação'), (29, 'Homologação inativa'), (30, 'Terceirizada cancelou solicitação de homologação de produto'), (25, 'CODAE suspendeu o produto'), (26, 'Escola/Nutricionista reclamou do produto'), (27, 'CODAE pediu análise da reclamação'), (28, 'CODAE autorizou reclamação'), (35, 'CODAE recusou reclamação'), (36, 'CODAE questionou terceirizada sobre reclamação'), (33, 'CODAE questionou U.E. sobre reclamação'), (37, 'CODAE respondeu ao reclamante da reclamação'), (31, 'Terceirizada respondeu a reclamação'), (34, 'U.E. respondeu a reclamação'), (32, 'Terceirizada respondeu a análise'), (39, 'Papa enviou a requisição'), (40, 'Dilog Enviou a requisição'), (41, 'Distribuidor confirmou requisição'), (42, 'Distribuidor pede alteração da requisição'), (43, 'Papa cancelou a requisição'), (44, 'Dilog Aceita Alteração'), (45, 'Dilog Nega Alteração'), (46, 'Cancelamento por alteração de unidade educacional'), (47, 'Cancelamento para aluno não matriculado na rede municipal')]),
        ),
    ]
