# Generated by Django 2.2.10 on 2020-05-14 17:20

import django_xworkflows.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0027_merge_20200504_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homologacaodoproduto',
            name='status',
            field=django_xworkflows.models.StateField(max_length=32, workflow=django_xworkflows.models._SerializedWorkflow(initial_state='CODAE_PENDENTE_HOMOLOGACAO', name='HomologacaoProdutoWorkflow', states=['RASCUNHO', 'CODAE_PENDENTE_HOMOLOGACAO', 'CODAE_HOMOLOGADO', 'CODAE_NAO_HOMOLOGADO', 'CODAE_QUESTIONADO', 'CODAE_PEDIU_ANALISE_SENSORIAL', 'TERCEIRIZADA_CANCELOU', 'CODAE_SUSPENDEU', 'ESCOLA_OU_NUTRICIONISTA_RECLAMOU', 'CODAE_PEDIU_ANALISE_RECLAMACAO', 'CODAE_AUTORIZOU_RECLAMACAO'])),
        ),
    ]
