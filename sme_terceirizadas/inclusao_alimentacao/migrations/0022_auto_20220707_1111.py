# Generated by Django 2.2.13 on 2022-07-07 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inclusao_alimentacao', '0021_auto_20220701_1414'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inclusaoalimentacaocontinua',
            name='observacao',
        ),
        migrations.AddField(
            model_name='quantidadeporperiodo',
            name='observacao',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Observação'),
        ),
    ]
