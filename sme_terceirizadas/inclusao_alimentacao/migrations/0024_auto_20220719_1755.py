# Generated by Django 2.2.13 on 2022-07-19 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inclusao_alimentacao', '0023_auto_20220714_0722'),
        ('paineis_consolidados', '0020_solicitacoes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quantidadeporperiodo',
            name='numero_alunos',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
