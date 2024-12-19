# Generated by Django 2.2.13 on 2021-11-10 20:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0021_substituicaoalimentacaonoperiodoescolar_qtd_alunos"),
    ]

    operations = [
        migrations.AddField(
            model_name="alteracaocardapio",
            name="terceirizada_conferiu_gestao",
            field=models.BooleanField(
                default=False, verbose_name="Terceirizada conferiu?"
            ),
        ),
        migrations.AddField(
            model_name="alteracaocardapiocei",
            name="terceirizada_conferiu_gestao",
            field=models.BooleanField(
                default=False, verbose_name="Terceirizada conferiu?"
            ),
        ),
        migrations.AddField(
            model_name="gruposuspensaoalimentacao",
            name="terceirizada_conferiu_gestao",
            field=models.BooleanField(
                default=False, verbose_name="Terceirizada conferiu?"
            ),
        ),
        migrations.AddField(
            model_name="inversaocardapio",
            name="terceirizada_conferiu_gestao",
            field=models.BooleanField(
                default=False, verbose_name="Terceirizada conferiu?"
            ),
        ),
    ]