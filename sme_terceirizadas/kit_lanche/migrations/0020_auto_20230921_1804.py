# Generated by Django 3.2.18 on 2023-09-21 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kit_lanche', '0019_solicitacaokitlanchecemei_evento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacaokitlancheavulsa',
            name='evento',
            field=models.CharField(blank=True, default='', max_length=160),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='solicitacaokitlancheceiavulsa',
            name='evento',
            field=models.CharField(blank=True, default='', max_length=160),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='solicitacaokitlanchecemei',
            name='evento',
            field=models.CharField(blank=True, default='', max_length=160),
            preserve_default=False,
        ),
    ]
