# Generated by Django 4.2.7 on 2024-12-18 15:10

from django.db import migrations, models


def converte_de_strins_vazia_para_null(apps, schema_editor):
    Contrato = apps.get_model("terceirizada", "Contrato")

    Contrato.objects.exclude(
        modalidade__in=["PREGAO_ELETRONICO", "CHAMADA_PUBLICA"]
    ).update(modalidade=None)


def converte_de_null_para_string_vazia(apps, schema_editor):
    Contrato = apps.get_model("terceirizada", "Contrato")

    Contrato.objects.exclude(
        modalidade__in=["PREGAO_ELETRONICO", "CHAMADA_PUBLICA"]
    ).update(modalidade="")


class Migration(migrations.Migration):
    dependencies = [
        ("terceirizada", "0021_modalidade"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contrato",
            name="modalidade",
            field=models.CharField(
                blank=True,
                choices=[
                    ("PREGAO_ELETRONICO", "Pregão Eletrônico"),
                    ("CHAMADA_PUBLICA", "Chamada Pública"),
                ],
                max_length=17,
                null=True,
            ),
        ),
        migrations.RunPython(
            converte_de_strins_vazia_para_null,
            reverse_code=converte_de_null_para_string_vazia,
        ),
    ]
