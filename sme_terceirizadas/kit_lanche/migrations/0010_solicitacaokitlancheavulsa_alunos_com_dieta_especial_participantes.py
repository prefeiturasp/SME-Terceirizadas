# Generated by Django 2.2.13 on 2021-11-23 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escola', '0044_auto_20211025_1759'),
        ('kit_lanche', '0009_remove_kitlanche_itens'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitacaokitlancheavulsa',
            name='alunos_com_dieta_especial_participantes',
            field=models.ManyToManyField(to='escola.Aluno'),
        ),
    ]
