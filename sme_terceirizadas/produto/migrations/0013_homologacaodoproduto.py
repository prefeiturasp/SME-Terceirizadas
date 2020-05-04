# Generated by Django 2.2.10 on 2020-04-23 18:36

import uuid

import django.db.models.deletion
import django_xworkflows.models
from django.conf import settings
from django.db import migrations, models

import sme_terceirizadas.dados_comuns.behaviors


class Migration(migrations.Migration):

    dependencies = [
        ('terceirizada', '0003_auto_20191213_1339'),
        ('escola', '0015_auto_20200313_1521'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('produto', '0012_auto_20200423_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomologacaoDoProduto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ativo', models.BooleanField(default=True, verbose_name='Está ativo?')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('status', django_xworkflows.models.StateField(max_length=29, workflow=django_xworkflows.models._SerializedWorkflow(initial_state='RASCUNHO', name='HomologacaoProdutoWorkflow', states=['RASCUNHO', 'CODAE_PENDENTE_HOMOLOGACAO', 'CODAE_HOMOLOGADO', 'CODAE_AUTORIZADO', 'CODAE_QUESTIONADO', 'CODAE_PEDIU_ANALISE_SENSORIAL', 'TERCEIRIZADA_CANCELOU']))),
                ('necessita_analise_sensorial', models.BooleanField(default=False)),
                ('criado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='homologacoes', to='produto.Produto')),
                ('rastro_lote', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='produto_homologacaodoproduto_rastro_lote', to='escola.Lote')),
                ('rastro_terceirizada', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='produto_homologacaodoproduto_rastro_terceirizada', to='terceirizada.Terceirizada')),
            ],
            options={
                'verbose_name': 'Homologação de Produto',
                'verbose_name_plural': 'Homologações de Produto',
                'ordering': ('-ativo', '-criado_em'),
            },
            bases=(django_xworkflows.models.BaseWorkflowEnabled, sme_terceirizadas.dados_comuns.behaviors.Logs, sme_terceirizadas.dados_comuns.behaviors.TemIdentificadorExternoAmigavel, models.Model),
        ),
    ]
