# Generated by Django 3.2.16 on 2023-03-06 13:56

from django.db import migrations
import django_xworkflows.models


class Migration(migrations.Migration):

    dependencies = [
        ('medicao_inicial', '0011_alter_solicitacaomedicaoinicial_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacaomedicaoinicial',
            name='status',
            field=django_xworkflows.models.StateField(max_length=39, workflow=django_xworkflows.models._SerializedWorkflow(initial_state='MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE', name='SolicitacaoMedicaoInicialWorkflow', states=['MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE', 'MEDICAO_ENVIADA_PELA_UE', 'MEDICAO_CORRECAO_SOLICITADA', 'MEDICAO_CORRECAO_SOLICITADA_CODAE', 'MEDICAO_CORRIGIDA_PELA_UE', 'MEDICAO_APROVADA_PELA_DRE', 'MEDICAO_APROVADA_PELA_CODAE'])),
        ),
    ]
