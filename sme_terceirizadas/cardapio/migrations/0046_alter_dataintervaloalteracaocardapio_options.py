# Generated by Django 3.2.18 on 2023-06-20 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cardapio', '0045_rename_dataalteracaocardapio_dataintervaloalteracaocardapio'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dataintervaloalteracaocardapio',
            options={'ordering': ('data',), 'verbose_name': 'Data do intervalo de Alteração de cardápio', 'verbose_name_plural': 'Datas do intervalo de Alteração de cardápio'},
        ),
    ]
