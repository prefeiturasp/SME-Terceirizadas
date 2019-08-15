# Generated by Django 2.0.13 on 2019-08-15 10:57

from django.db import migrations
import django_xworkflows.models


class Migration(migrations.Migration):

    dependencies = [
        ('kit_lanche', '0003_solicitacaokitlancheavulsa_criado_por'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacaokitlancheavulsa',
            name='status',
            field=django_xworkflows.models.StateField(max_length=25, workflow=django_xworkflows.models._SerializedWorkflow(initial_state='RASCUNHO', name='PedidoAPartirDaEscolaWorkflow', states=['RASCUNHO', 'DRE_A_VALIDAR', 'DRE_APROVADO', 'DRE_PEDE_ESCOLA_REVISAR', 'CODAE_APROVADO', 'CODAE_RECUSOU', 'TERCEIRIZADA_TOMA_CIENCIA'])),
        ),
        migrations.AlterField(
            model_name='solicitacaokitlancheunificada',
            name='status',
            field=django_xworkflows.models.StateField(max_length=25, workflow=django_xworkflows.models._SerializedWorkflow(initial_state='RASCUNHO', name='PedidoAPartirDaDiretoriaRegionalWorkflow', states=['RASCUNHO', 'CODAE_A_VALIDAR', 'DRE_PEDE_DRE_REVISAR', 'CODAE_APROVADO', 'TERCEIRIZADA_TOMA_CIENCIA'])),
        ),
    ]
