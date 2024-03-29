# Generated by Django 2.2.13 on 2023-01-11 14:29

import django.core.validators
from django.db import migrations, models


def popular_posicao(apps, _):
    TipoAlimentacao = apps.get_model("cardapio", "TipoAlimentacao")
    TipoAlimentacao.objects.filter(nome="Lanche 4h").update(posicao=1)
    TipoAlimentacao.objects.filter(nome="Lanche").update(posicao=2)
    TipoAlimentacao.objects.filter(nome="Refeição").update(posicao=3)
    TipoAlimentacao.objects.filter(nome="Sobremesa").update(posicao=4)


def backwards(apps, _):
    TipoAlimentacao = apps.get_model("cardapio", "TipoAlimentacao")
    TipoAlimentacao.objects.update(posicao=None)


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0041_auto_20221221_1140"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipoalimentacao",
            name="posicao",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
        migrations.RunPython(popular_posicao, backwards),
    ]
