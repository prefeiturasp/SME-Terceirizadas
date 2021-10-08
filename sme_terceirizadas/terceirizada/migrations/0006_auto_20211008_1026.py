# Generated by Django 2.2.13 on 2021-10-08 10:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terceirizada', '0005_auto_20201127_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='terceirizada',
            name='criado_em',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 8, 10, 26, 10, 343908), editable=False, verbose_name='Criado em'),
        ),
        migrations.AddField(
            model_name='terceirizada',
            name='numero_contrato',
            field=models.CharField(blank=True, max_length=50, verbose_name='Número de contrato'),
        ),
        migrations.AddField(
            model_name='terceirizada',
            name='tipo_alimento',
            field=models.CharField(choices=[('CONGELADOS_E_RESFRIADOS', 'Congelados e resfriados'), ('FLVO', 'FLVO'), ('PAES_E_BOLO', 'Pães & bolos'), ('SECOS', 'Secos')], default='TERCEIRIZADA', max_length=25),
        ),
        migrations.AddField(
            model_name='terceirizada',
            name='tipo_empresa',
            field=models.CharField(choices=[('ARMAZEM/DISTRIBUIDOR', 'Armazém/Distribuidor'), ('FORNECEDOR/DISTRIBUIDOR', 'Fornecedor/Distribuidor'), ('TERCEIRIZADA', 'Terceirizada')], default='TERCEIRIZADA', max_length=25),
        ),
    ]
