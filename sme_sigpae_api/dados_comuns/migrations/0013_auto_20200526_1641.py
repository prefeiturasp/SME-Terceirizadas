# Generated by Django 2.2.10 on 2020-05-26 19:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dados_comuns", "0012_auto_20200429_1007"),
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
                    (14, "DRE cancelou"),
                    (11, "Questionamento pela CODAE"),
                    (12, "Terceirizada respondeu questionamento"),
                    (15, "Escola solicitou inativação"),
                    (16, "CODAE autorizou inativação"),
                    (17, "CODAE negou inativação"),
                    (18, "Terceirizada tomou ciência da inativação"),
                    (19, "Terminada por atingir data de término"),
                    (20, "Pendente homologação da CODAE"),
                    (21, "CODAE homologou"),
                    (22, "CODAE não homologou"),
                    (23, "CODAE pediu análise sensorial"),
                    (24, "Terceirizada cancelou homologação"),
                    (29, "Homologação inativa"),
                    (25, "CODAE suspendeu o produto"),
                    (26, "Escola/Nutricionista reclamou do produto"),
                    (27, "CODAE pediu análise da reclamação"),
                    (28, "CODAE autorizou reclamação"),
                ]
            ),
        ),
    ]