# Generated by Django 2.2.13 on 2021-10-08 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cardapio', '0019_substituicaoalimentacaonoperiodoescolar_qtd_alunos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='substituicaoalimentacaonoperiodoescolar',
            name='qtd_alunos',
        ),
    ]
