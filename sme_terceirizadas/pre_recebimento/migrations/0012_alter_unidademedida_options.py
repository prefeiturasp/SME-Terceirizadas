# Generated by Django 3.2.18 on 2023-07-20 18:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pre_recebimento', '0011_unidademedida'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unidademedida',
            options={'ordering': ('-criado_em',), 'verbose_name': 'Unidade de Medida', 'verbose_name_plural': 'Unidades de Medida'},
        ),
    ]
