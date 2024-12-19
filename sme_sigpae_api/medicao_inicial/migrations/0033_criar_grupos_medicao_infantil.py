# Generated by Django 2.2.13 on 2023-01-20 17:06

from django.db import migrations


def inserir_nomes(apps, _):
    GrupoMedicao = apps.get_model("medicao_inicial", "GrupoMedicao")
    for nome in ["Infantil INTEGRAL", "Infantil MANHA", "Infantil TARDE"]:
        GrupoMedicao.objects.create(nome=nome)


def backwards(apps, _):
    GrupoMedicao = apps.get_model("medicao_inicial", "GrupoMedicao")
    GrupoMedicao.objects.filter(nome__icontains="Infantil").delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "medicao_inicial",
            "0032_remove_solicitacaomedicaoinicial_tipo_contagem_alimentacoes_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(inserir_nomes, backwards),
    ]