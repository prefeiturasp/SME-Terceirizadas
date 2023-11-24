# Generated by Django 4.1.12 on 2023-11-23 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dieta_especial', '0057_alter_solicitacaodietaespecial_rastro_dre_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='logquantidadedietasautorizadas',
            name='cei_ou_emei',
            field=models.CharField(choices=[('N/A', 'N/A'), ('CEI', 'CEI'), ('EMEI', 'EMEI')], default='N/A', max_length=4),
        ),
    ]
