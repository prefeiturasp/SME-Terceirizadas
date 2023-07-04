# Generated by Django 3.2.16 on 2023-02-21 04:29

from django.db import migrations, models
import django.db.models.deletion


def adiciona_motivos_inclusao_alimentacao(apps, _):
    modelo_motivo_inclusao_continua = apps.get_model('inclusao_alimentacao', 'MotivoInclusaoContinua')
    modelo_motivo_inclusao_normal = apps.get_model('inclusao_alimentacao', 'MotivoInclusaoNormal')
    modelo_motivo_inclusao_continua.objects.create(
        nome="Programas/Projetos Específicos"
    )
    modelo_motivo_inclusao_normal.objects.create(
        nome="Evento Específico"
    )

def backwards(apps, _):
    modelo_motivo_inclusao_continua = apps.get_model('inclusao_alimentacao', 'MotivoInclusaoContinua')
    modelo_motivo_inclusao_normal = apps.get_model('inclusao_alimentacao', 'MotivoInclusaoNormal')
    modelo_motivo_inclusao_continua.objects.filter(
        nome="Programas/Projetos Específicos"
    ).delete()
    modelo_motivo_inclusao_normal.objects.filter(
        nome="Evento Específico"
    ).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('inclusao_alimentacao', '0033_quantidadedealunosporfaixaetariadainclusaodealimentacaodacei_periodo_externo'),
    ]

    operations = [
        migrations.RunPython(adiciona_motivos_inclusao_alimentacao, backwards),
    ]
