# Generated by Django 2.2.8 on 2019-12-19 19:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0007_inversaocardapio_foi_solicitado_fora_do_prazo"),
    ]

    operations = [
        migrations.AddField(
            model_name="vinculotipoalimentacaocomperiodoescolaretipounidadeescolar",
            name="ativo",
            field=models.BooleanField(default=True, verbose_name="Está ativo?"),
        ),
    ]
