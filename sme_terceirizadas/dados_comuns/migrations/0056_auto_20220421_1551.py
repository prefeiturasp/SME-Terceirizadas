# Generated by Django 2.2.13 on 2022-04-21 15:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0055_auto_20220324_1238"),
    ]

    operations = [
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
                    (14, "CODAE negou cancelamento"),
                    (15, "DRE cancelou"),
                    (11, "Questionamento pela CODAE"),
                    (12, "Terceirizada respondeu questionamento"),
                    (16, "Escola solicitou cancelamento"),
                    (17, "CODAE autorizou cancelamento"),
                    (18, "CODAE negou cancelamento"),
                    (19, "Terceirizada tomou ciência do cancelamento"),
                    (20, "Cancelada por atingir data de término"),
                    (21, "Pendente homologação da CODAE"),
                    (22, "CODAE homologou"),
                    (23, "CODAE não homologou"),
                    (24, "CODAE pediu análise sensorial"),
                    (25, "CODAE cancelou análise sensorial"),
                    (26, "Terceirizada cancelou homologação"),
                    (31, "Homologação inativa"),
                    (32, "Terceirizada cancelou solicitação de homologação de produto"),
                    (27, "CODAE suspendeu o produto"),
                    (28, "Escola/Nutricionista reclamou do produto"),
                    (29, "CODAE pediu análise da reclamação"),
                    (30, "CODAE autorizou reclamação"),
                    (39, "CODAE recusou reclamação"),
                    (40, "CODAE questionou terceirizada sobre reclamação"),
                    (35, "CODAE questionou U.E. sobre reclamação"),
                    (41, "CODAE respondeu ao reclamante da reclamação"),
                    (38, "CODAE questionou nutrisupervisor sobre reclamação"),
                    (33, "Terceirizada respondeu a reclamação"),
                    (36, "U.E. respondeu a reclamação"),
                    (37, "Nutrisupervisor respondeu a reclamação"),
                    (34, "Terceirizada respondeu a análise"),
                    (43, "Papa enviou a requisição"),
                    (44, "Dilog Enviou a requisição"),
                    (45, "Distribuidor confirmou requisição"),
                    (46, "Distribuidor pede alteração da requisição"),
                    (47, "Papa cancelou a requisição"),
                    (48, "Papa aguarda confirmação do cancelamento da solicitação"),
                    (
                        49,
                        "Distribuidor confirmou cancelamento e Papa cancelou a requisição",
                    ),
                    (50, "Dilog Aceita Alteração"),
                    (51, "Dilog Nega Alteração"),
                    (52, "Cancelamento por alteração de unidade educacional"),
                    (53, "Cancelamento para aluno não matriculado na rede municipal"),
                ]
            ),
        ),
    ]
