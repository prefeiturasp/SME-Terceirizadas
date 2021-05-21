# Generated by Django 2.2.13 on 2021-05-21 17:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logistica', '0030_conferenciaguia_criado_por'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conferenciaguia',
            name='nome_motorista',
            field=models.CharField(max_length=100, verbose_name='Nome do motorista'),
        ),
        migrations.AlterField(
            model_name='conferenciaguia',
            name='placa_veiculo',
            field=models.CharField(max_length=7, verbose_name='Placa do veículo'),
        ),
        migrations.CreateModel(
            name='InsucessoEntregaGuia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('hora_tentativa', models.TimeField(verbose_name='Hora da tentativa de entrega')),
                ('nome_motorista', models.CharField(max_length=100, verbose_name='Nome do motorista')),
                ('placa_veiculo', models.CharField(max_length=7, verbose_name='Placa do veículo')),
                ('justificativa', models.TextField(max_length=500, verbose_name='Justificativa')),
                ('arquivo', models.FileField(upload_to='')),
                ('motivo', models.CharField(choices=[('UNIDADE_FECHADA', 'Unidade educacional fechada'), ('OUTROS', 'Outros')], default='UNIDADE_FECHADA', max_length=25, verbose_name='Status da guia')),
                ('criado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('guia', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='insucessos', to='logistica.Guia')),
            ],
            options={
                'verbose_name': 'Conferência da Guia de Remessa',
                'verbose_name_plural': 'Conferência das Guias de Remessas',
            },
        ),
    ]
