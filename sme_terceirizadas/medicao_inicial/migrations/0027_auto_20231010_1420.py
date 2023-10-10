# Generated by Django 3.2.20 on 2023-10-10 14:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sme_terceirizadas.dados_comuns.behaviors
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('escola', '0062_diasuspensaoatividades'),
        ('medicao_inicial', '0026_alimentacaolancamentoespecial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alimentacaolancamentoespecial',
            options={'ordering': ['posicao'], 'verbose_name': 'Alimentação de Lançamento Especial', 'verbose_name_plural': 'Alimentações de Lançamentos Especiais'},
        ),
        migrations.CreateModel(
            name='PermissaoLancamentoEspecial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data_inicial', models.DateField(blank=True, null=True, verbose_name='Data inicial')),
                ('data_final', models.DateField(blank=True, null=True, verbose_name='Data final')),
                ('alimentacoes_lancamento_especial', models.ManyToManyField(to='medicao_inicial.AlimentacaoLancamentoEspecial')),
                ('criado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('diretoria_regional', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='permissoes_lancamento_especial', to='escola.diretoriaregional')),
                ('escola', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissoes_lancamento_especial', to='escola.escola')),
                ('periodo_escolar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='escola.periodoescolar')),
            ],
            options={
                'verbose_name': 'Permissão de Lançamento Especial',
                'verbose_name_plural': 'Permissões de Lançamentos Especiais',
            },
            bases=(models.Model, sme_terceirizadas.dados_comuns.behaviors.TemIdentificadorExternoAmigavel),
        ),
    ]
