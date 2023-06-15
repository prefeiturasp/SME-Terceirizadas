# Generated by Django 3.2.18 on 2023-06-06 15:49

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0049_auto_20230606_1549'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrevisaoContratualNotificacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('tipo_ocorrencia', models.CharField(blank=True, choices=[('QTD_MENOR', 'Quantidade menor que a prevista'), ('PROBLEMA_QUALIDADE', 'Problema de qualidade do produto'), ('ALIMENTO_DIFERENTE', 'Alimento diferente do previsto'), ('EMBALAGEM_DANIFICADA', 'Embalagem danificada'), ('EMBALAGEM_VIOLADA', 'Embalagem violada'), ('VALIDADE_EXPIRADA', 'Prazo de validade expirado'), ('ATRASO_ENTREGA', 'Atraso na entrega'), ('AUSENCIA_PRODUTO', 'Ausência do produto'), ('FALTA_URBANIDADE', 'Falta de urbanidade na entrega'), ('FALTA_ESPACO_ARMAZENAMENTO', 'Falta de espaço no freezer para armazenamento')], max_length=40)),
                ('previsao_contratual', models.TextField(blank=True, max_length=500, verbose_name='Previsão Contratual')),
                ('notificacao', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='previsoes_contratuais', to='logistica.notificacaoocorrenciasguia')),
            ],
            options={
                'verbose_name': 'Previsão Contratual',
                'verbose_name_plural': 'Previsões Contratuais',
            },
        ),
    ]