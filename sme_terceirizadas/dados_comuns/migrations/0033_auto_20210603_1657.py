# Generated by Django 2.2.13 on 2021-06-03 16:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0032_auto_20210520_1527"),
    ]

    operations = [
        migrations.AlterField(
            model_name="logsolicitacoesusuario",
            name="solicitacao_tipo",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Solicitação de kit lanche avulsa"),
                    (1, "Alteração do tipo de alimentação"),
                    (2, "Suspensão de cardápio"),
                    (3, "Inversão de cardápio"),
                    (4, "Inclusão de alimentação normal"),
                    (5, "Inclusão de alimentação da CEI"),
                    (6, "Suspensão de alimentação da CEI"),
                    (7, "Inclusão de alimentação contínua"),
                    (8, "Dieta Especial"),
                    (9, "Solicitação de kit lanche unificada"),
                    (10, "Homologação de Produto"),
                    (11, "Reclamação de Produto"),
                    (32, "Responde Análise Sensorial"),
                    (12, "Solicitação de remessa"),
                    (13, "Solicitação de Ateração de requisição"),
                    (14, "Abastecimento de guia de remessa"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="logsolicitacoesusuario",
            name="status_evento",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Solicitação Realizada"),
                    (1, "CODAE autorizou"),
                    (2, "Terceirizada tomou ciência"),
                    (3, "Terceirizada recusou"),
                    (4, "CODAE negou"),
                    (5, "CODAE pediu revisão"),
                    (6, "DRE revisou"),
                    (7, "DRE validou"),
                    (8, "DRE pediu revisão"),
                    (9, "DRE não validou"),
                    (10, "Escola revisou"),
                    (13, "Escola cancelou"),
                    (14, "DRE cancelou"),
                    (11, "Questionamento pela CODAE"),
                    (12, "Terceirizada respondeu questionamento"),
                    (15, "Escola solicitou inativação"),
                    (16, "CODAE autorizou inativação"),
                    (17, "CODAE negou inativação"),
                    (18, "Terceirizada tomou ciência da inativação"),
                    (19, "Cancelada por atingir data de término"),
                    (20, "Pendente homologação da CODAE"),
                    (21, "CODAE homologou"),
                    (22, "CODAE não homologou"),
                    (23, "CODAE pediu análise sensorial"),
                    (24, "Terceirizada cancelou homologação"),
                    (29, "Homologação inativa"),
                    (30, "Terceirizada cancelou solicitação de homologação de produto"),
                    (25, "CODAE suspendeu o produto"),
                    (26, "Escola/Nutricionista reclamou do produto"),
                    (27, "CODAE pediu análise da reclamação"),
                    (28, "CODAE autorizou reclamação"),
                    (33, "CODAE recusou reclamação"),
                    (34, "CODAE questionou terceirizada sobre reclamação"),
                    (35, "CODAE respondeu ao reclamante da reclamação"),
                    (31, "Terceirizada respondeu a reclamação"),
                    (32, "Terceirizada respondeu a análise"),
                    (37, "Papa enviou a requisição"),
                    (38, "Dilog Enviou a requisição"),
                    (39, "Distribuidor confirmou requisição"),
                    (40, "Distribuidor pede alteração da requisição"),
                    (41, "Papa cancelou a requisição"),
                    (42, "Dilog Aceita Alteração"),
                    (43, "Dilog Nega Alteração"),
                    (44, "Cancelamento por alteração de unidade educacional"),
                    (45, "Cancelamento para aluno não matriculado na rede municipal"),
                ]
            ),
        ),
    ]
