# Generated by Django 2.2.8 on 2020-04-23 18:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dieta_especial', '0011_auto_20200226_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='substituicaoalimento',
            name='alimento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dieta_especial.Alimento'),
        ),
        migrations.AlterField(
            model_name='substituicaoalimento',
            name='tipo',
            field=models.CharField(blank=True, choices=[('I', 'Isento'), ('S', 'Substituir')], max_length=1),
        ),
    ]
