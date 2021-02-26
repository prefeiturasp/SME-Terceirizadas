# Generated by Django 2.2.13 on 2021-02-26 17:48

import django_xworkflows.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0017_solicitacaodealteracaorequisicao_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitacaoremessa',
            name='quantidade_total_guias',
            field=models.IntegerField(null=True, verbose_name='Qtd total de guias na requisição'),
        ),
        migrations.AlterField(
            model_name='solicitacaodealteracaorequisicao',
            name='status',
            field=django_xworkflows.models.StateField(max_length=16, workflow=django_xworkflows.models._SerializedWorkflow(initial_state='EM_ANALISE', name='SolicitacaoDeAlteracaoWorkFlow', states=['EM_ANALISE', 'ACEITA', 'NEGADA'])),
        ),
    ]
