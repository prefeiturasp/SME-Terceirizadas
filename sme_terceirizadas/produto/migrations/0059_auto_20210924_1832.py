# Generated by Django 2.2.13 on 2021-09-24 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produto', '0058_embalagem_unidademedida'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Embalagem',
            new_name='EmbalagemProduto',
        ),
    ]
