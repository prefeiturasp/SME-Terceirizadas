# Generated by Django 2.2.13 on 2021-04-07 10:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0017_alteracaocardapiocei_eh_alteracao_com_lanche_repetida"),
    ]

    operations = [
        migrations.AlterField(
            model_name="suspensaoalimentacao",
            name="outro_motivo",
            field=models.CharField(
                blank=True, max_length=500, verbose_name="Outro motivo"
            ),
        ),
        migrations.AlterField(
            model_name="suspensaoalimentacaodacei",
            name="outro_motivo",
            field=models.CharField(
                blank=True, max_length=500, verbose_name="Outro motivo"
            ),
        ),
    ]
