# Generated by Django 2.2.13 on 2023-01-06 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('terceirizada', '0009_auto_20221221_0921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='terceirizada',
            name='eh_distribuidor',
        ),
        migrations.RemoveField(
            model_name='terceirizada',
            name='numero_contrato',
        ),
        migrations.RemoveField(
            model_name='terceirizada',
            name='tipo_empresa',
        ),
        migrations.AddField(
            model_name='terceirizada',
            name='tipo_servico',
            field=models.CharField(choices=[('TERCEIRIZADA', 'Terceirizada'), ('DISTRIBUIDOR_ARMAZEM', 'Distribuidor (Armazém)'), ('FORNECEDOR', 'Fornecedor'), ('FORNECEDOR_E_DISTRIBUIDOR', 'Fornecedor e Distribuidor')], default='TERCEIRIZADA', max_length=25),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='data_proposta',
            field=models.DateField(blank=True, null=True, verbose_name='Data da proposta'),
        ),
    ]
