# Generated by Django 2.2.8 on 2020-02-10 14:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0011_auto_20200204_1341"),
    ]

    operations = [
        migrations.AlterField(
            model_name="quantidadeporperiodosuspensaoalimentacao",
            name="tipos_alimentacao",
            field=models.ManyToManyField(
                to="cardapio.ComboDoVinculoTipoAlimentacaoPeriodoTipoUE"
            ),
        ),
    ]
