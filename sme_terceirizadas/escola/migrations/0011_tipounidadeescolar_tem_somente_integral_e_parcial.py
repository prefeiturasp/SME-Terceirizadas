# Generated by Django 2.2.8 on 2020-02-13 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escola', '0010_auto_20200122_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipounidadeescolar',
            name='tem_somente_integral_e_parcial',
            field=models.BooleanField(default=False, help_text='Variável de controle para setar os períodos escolares na mão, válido para CEI CEU, CEI e CCI'),
        ),
    ]
