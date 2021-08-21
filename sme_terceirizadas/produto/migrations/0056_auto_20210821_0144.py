# Generated by Django 2.2.13 on 2021-08-21 01:44

from django.db import migrations
import django_xworkflows.models


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0055_auto_20210818_0252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homologacaodoproduto',
            name='status',
            field=django_xworkflows.models.StateField(max_length=45, workflow=django_xworkflows.models._SerializedWorkflow(initial_state='RASCUNHO', name='HomologacaoProdutoWorkflow', states=['RASCUNHO', 'CODAE_PENDENTE_HOMOLOGACAO', 'CODAE_HOMOLOGADO', 'CODAE_NAO_HOMOLOGADO', 'CODAE_QUESTIONADO', 'CODAE_PEDIU_ANALISE_SENSORIAL', 'TERCEIRIZADA_CANCELOU', 'HOMOLOGACAO_INATIVA', 'CODAE_SUSPENDEU', 'ESCOLA_OU_NUTRICIONISTA_RECLAMOU', 'CODAE_QUESTIONOU_UE', 'UE_RESPONDEU_QUESTIONAMENTO', 'CODAE_QUESTIONOU_NUTRISUPERVISOR', 'NUTRISUPERVISOR_RESPONDEU_QUESTIONAMENTO', 'CODAE_PEDIU_ANALISE_RECLAMACAO', 'TERCEIRIZADA_RESPONDEU_RECLAMACAO', 'CODAE_AUTORIZOU_RECLAMACAO', 'TERCEIRIZADA_CANCELOU_SOLICITACAO_HOMOLOGACAO'])),
        ),
        migrations.AlterField(
            model_name='reclamacaodeproduto',
            name='status',
            field=django_xworkflows.models.StateField(max_length=35, workflow=django_xworkflows.models._SerializedWorkflow(initial_state='AGUARDANDO_AVALIACAO', name='ReclamacaoProdutoWorkflow', states=['AGUARDANDO_AVALIACAO', 'AGUARDANDO_RESPOSTA_TERCEIRIZADA', 'AGUARDANDO_RESPOSTA_UE', 'AGUARDANDO_RESPOSTA_NUTRISUPERVISOR', 'AGUARDANDO_ANALISE_SENSORIAL', 'ANALISE_SENSORIAL_RESPONDIDA', 'RESPONDIDO_TERCEIRIZADA', 'RESPONDIDO_UE', 'RESPONDIDO_NUTRISUPERVISOR', 'CODAE_ACEITOU', 'CODAE_RECUSOU', 'CODAE_RESPONDEU'])),
        ),
    ]
