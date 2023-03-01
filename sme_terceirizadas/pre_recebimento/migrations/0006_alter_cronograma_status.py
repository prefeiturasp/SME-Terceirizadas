# Generated by Django 3.2.16 on 2023-03-01 11:00

from django.db import migrations
import django_xworkflows.models

def atualiza_status(apps, _):
    Cronograma = apps.get_model("pre_recebimento", "Cronograma")
    Cronograma.objects.filter(status='ASSINADO_CRONOGRAMA').update(status='ASSINADO_E_ENVIADO_AO_FORNECEDOR')
    Cronograma.objects.filter(status='ENVIADO_AO_FORNECEDOR').update(status='ASSINADO_E_ENVIADO_AO_FORNECEDOR')


def backwards(apps, _):
    Cronograma = apps.get_model("pre_recebimento", "Cronograma")
    Cronograma.objects.filter(status='ASSINADO_E_ENVIADO_AO_FORNECEDOR').update(status='ASSINADO_CRONOGRAMA')
    Cronograma.objects.filter(status='ASSINADO_E_ENVIADO_AO_FORNECEDOR').update(status='ENVIADO_AO_FORNECEDOR')


class Migration(migrations.Migration):

    dependencies = [
        ('pre_recebimento', '0005_alter_cronograma_status'),
    ]

    operations = [
        migrations.RunPython(atualiza_status, backwards),
        migrations.AlterField(
            model_name='cronograma',
            name='status',
            field=django_xworkflows.models.StateField(max_length=32, workflow=django_xworkflows.models._SerializedWorkflow(initial_state='RASCUNHO', name='CronogramaWorkflow', states=['RASCUNHO', 'ASSINADO_E_ENVIADO_AO_FORNECEDOR', 'ALTERACAO_CODAE', 'APROVADO', 'REPROVADO', 'ALTERACAO_FORNECEDOR', 'ASSINADO_FORNECEDOR', 'SOLICITADO_ALTERACAO', 'ASSINADO_DINUTRE'])),
        ),
    ]
