# Generated by Django 2.2.8 on 2020-01-29 18:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "inclusao_alimentacao",
            "0005_grupoinclusaoalimentacaonormal_foi_solicitado_fora_do_prazo",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="quantidadeporperiodo",
            name="tipos_alimentacao",
            field=models.ManyToManyField(
                to="cardapio.ComboDoVinculoTipoAlimentacaoPeriodoTipoUE"
            ),
        ),
    ]
