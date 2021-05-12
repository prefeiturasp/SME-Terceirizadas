# Generated by Django 2.2.13 on 2021-05-12 18:03

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('logistica', '0028_auto_20210427_1247'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConferenciaGuia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data_recebimento', models.DateField(verbose_name='Data de recebimento')),
                ('hora_recebimento', models.TimeField(verbose_name='Hora do recebimento')),
                ('nome_motorista', models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(message='Digite apenas letras', regex='/[a-zA-Z]+/g')], verbose_name='Nome do motorista')),
                ('placa_veiculo', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(message='Digite apenas letras e números', regex='/[^A-Za-z0-9]+/g')], verbose_name='Placa do veículo')),
                ('guia', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='conferencias', to='logistica.Guia')),
            ],
            options={
                'verbose_name': 'Conferência da Guia de Remessa',
                'verbose_name_plural': 'Conferência das Guias de Remessas',
            },
        ),
    ]
