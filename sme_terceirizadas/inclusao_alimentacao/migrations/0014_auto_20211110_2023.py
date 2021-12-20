# Generated by Django 2.2.13 on 2021-11-10 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inclusao_alimentacao', '0013_auto_20210406_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupoinclusaoalimentacaonormal',
            name='terceirizada_conferiu_gestao',
            field=models.BooleanField(default=False, verbose_name='Terceirizada conferiu?'),
        ),
        migrations.AddField(
            model_name='inclusaoalimentacaocontinua',
            name='terceirizada_conferiu_gestao',
            field=models.BooleanField(default=False, verbose_name='Terceirizada conferiu?'),
        ),
        migrations.AddField(
            model_name='inclusaoalimentacaodacei',
            name='terceirizada_conferiu_gestao',
            field=models.BooleanField(default=False, verbose_name='Terceirizada conferiu?'),
        ),
    ]
